"""Install the daily agent as a bounded systemd oneshot on Ubuntu/Debian."""

import argparse
import json
import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", required=True)
    parser.add_argument("--author-name", required=True)
    parser.add_argument("--author-email", required=True)
    parser.add_argument(
        "--git-url",
        default="https://github.com/KinvyPhanyel/projets.git",
        choices=[
            "https://github.com/KinvyPhanyel/projets.git",
            "git@github.com:KinvyPhanyel/projets.git",
        ],
    )
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error("Lancer avec sudo pour installer les unités système")
    if sys.version_info < (3, 12):
        parser.error("Python 3.12+ requis")
    if not re.fullmatch(r"[a-z_][a-z0-9_-]*", args.user):
        parser.error("Utilisateur invalide")
    account = pwd.getpwnam(args.user)
    if account.pw_uid == 0:
        parser.error("Le service ne doit pas exécuter les tests en root")
    if not re.fullmatch(r"[^\s<>]+@[^\s<>]+", args.author_email):
        parser.error("Adresse Git vérifiée requise")
    if not args.author_name.strip() or "\n" in args.author_name:
        parser.error("Nom d’auteur invalide")
    for tool in ["git", "systemctl", "systemd-analyze", "runuser"]:
        if not shutil.which(tool):
            parser.error("Outil requis absent : " + tool)
    subprocess.run(
        ["/usr/bin/python3", "-c", "import sys; assert sys.version_info >= (3,12)"], check=True
    )
    home = Path(account.pw_dir)
    if not re.fullmatch(r"/[A-Za-z0-9/_-]+", str(home)):
        parser.error("Chemin utilisateur non pris en charge")
    state = home / ".local/state/portfolio-agent"
    repo = state / "repository"
    runtime = state / "runtime"
    configdir = home / ".config/portfolio-agent"
    config = configdir / "config.json"
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_SSH_COMMAND="ssh -o BatchMode=yes")

    def as_user(*command, timeout=90):
        subprocess.run(
            ["runuser", "-u", args.user, "--", *map(str, command)],
            check=True,
            env=env,
            timeout=timeout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Create only dedicated paths; never reuse another application's checkout.
    for path in [
        home / ".local",
        home / ".local/state",
        state,
        runtime,
        home / ".config",
        configdir,
    ]:
        if path.is_symlink():
            parser.error("Lien symbolique refusé dans les chemins de service")
        if not path.exists():
            path.mkdir(mode=0o700)
            os.chown(path, account.pw_uid, account.pw_gid)
        elif path.stat().st_uid != account.pw_uid:
            parser.error("Dossier non détenu par l’utilisateur : " + str(path))
    try:
        if repo.exists():
            if repo.is_symlink():
                parser.error("Clone dédié requis")
            remote = subprocess.run(
                [
                    "runuser",
                    "-u",
                    args.user,
                    "--",
                    "git",
                    "-C",
                    str(repo),
                    "remote",
                    "get-url",
                    "origin",
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            if remote != args.git_url:
                parser.error("Le clone existant a une autre origine")
        else:
            as_user(
                "git",
                "clone",
                "--single-branch",
                "--branch",
                "portfolio-projets",
                args.git_url,
                repo,
            )
        if not (repo / "automation/daily/agent.py").is_file():
            parser.error("La branche distante doit contenir la version de l’agent")
        as_user(
            "git", "-C", repo, "push", "--dry-run", "origin", "HEAD:refs/heads/portfolio-projets"
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        parser.error(
            "Accès GitHub non interactif inutilisable : configurer une authentification de ce compte avec droit d’écriture sur ce seul dépôt"
        )
    proposed = {
        "repository": str(repo),
        "state_directory": str(runtime),
        "branch": "portfolio-projets",
        "author_name": args.author_name,
        "author_email": args.author_email,
        "timezone": "Africa/Douala",
        "retention_days": 90,
    }
    if config.exists():
        if config.is_symlink() or json.loads(config.read_text()) != proposed:
            parser.error(
                "Configuration existante différente : conservée, modifier explicitement avant de relancer"
            )
    else:
        descriptor = os.open(config, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(proposed, stream, indent=2)
        os.chown(config, account.pw_uid, account.pw_gid)
    units = Path("/etc/systemd/system")
    template = (repo / "automation/daily/systemd/portfolio-maintenance.service.in").read_text()
    for key, value in {
        "USER": args.user,
        "REPO": str(repo),
        "CONFIG": str(config),
        "STATE": str(state),
    }.items():
        template = template.replace("@" + key + "@", value)
    timer = (repo / "automation/daily/systemd/portfolio-maintenance.timer").read_text()
    subprocess.run(
        ["systemd-analyze", "calendar", "*-*-* 19:00:00 Africa/Douala"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    for name, text in [
        ("portfolio-maintenance.service", template),
        ("portfolio-maintenance.timer", timer),
    ]:
        destination = units / name
        if destination.is_symlink():
            parser.error("Unité existante en lien symbolique : conservée")
        if destination.exists() and destination.read_text() != text:
            backup = destination.with_name(destination.name + ".backup-" + str(time.time_ns()))
            shutil.copy2(destination, backup)
        destination.write_text(text)
        destination.chmod(0o644)
    subprocess.run(
        [
            "systemd-analyze",
            "verify",
            str(units / "portfolio-maintenance.service"),
            str(units / "portfolio-maintenance.timer"),
        ],
        check=True,
    )
    # Verify and publish once before enabling recurring execution.
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "start", "portfolio-maintenance.service"], check=True, timeout=500)
    subprocess.run(["systemctl", "enable", "--now", "portfolio-maintenance.timer"], check=True)
    print(
        "Premier contrôle publié. Minuteur activé : 19 h à Douala, avec un décalage maximal de 15 minutes."
    )


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(
            "Installation interrompue ; consulter l’état du service. Aucun redémarrage applicatif effectué.",
            file=sys.stderr,
        )
        raise SystemExit(1)
