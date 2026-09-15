#!/usr/bin/env python3
"""
mirth2john - Convertit les hashes Mirth Connect au format John the Ripper.

Supporte les formats :
  - Legacy  : SHA256 salé, 1000 itérations (Mirth <= 4.3)
  - Moderne : PBKDF2WithHmacSHA256, 600000 itérations (Mirth >= 4.4.0)

Usage:
  mirth2john -h 'hash_base64'              # hash unique vers stdout
  mirth2john -f entree.txt -o sortie.txt   # conversion par lot
  mirth2john --legacy -h 'hash_base64'     # forcer le format legacy
"""

import argparse
import base64
import sys

# ------------------------------
# Configuration
# ------------------------------
LEGACY_SALT_SIZE = 8
LEGACY_ITERATIONS = 1000
LEGACY_ALGO = "sha256"

MODERN_SALT_SIZE = 8
MODERN_ITERATIONS = 600000
MODERN_ALGO = "pbkdf2-sha256"


# ------------------------------
# Fonctions utilitaires
# ------------------------------
def decode_base64_hash(encoded: str):
    """Décode un hash Mirth en Base64, tolérant les espaces et padding manquant."""
    encoded = encoded.strip()
    if not encoded:
        return None
    padding = 4 - (len(encoded) % 4)
    if padding != 4:
        encoded += "=" * padding
    try:
        return base64.b64decode(encoded)
    except Exception:
        return None


def detect_hash_type(raw: bytes):
    """
    Détecte le format Mirth à partir des octets décodés.
    Retourne 'legacy', 'modern' ou None.
    """
    if len(raw) == 40:
        # Les deux formats font 40 octets (8 sel + 32 hash)
        # Par défaut on suppose moderne (Mirth >= 4.4)
        return "modern"
    return None


# ------------------------------
# Conversion
# ------------------------------
def convert_legacy(raw: bytes) -> str:
    """Format legacy : SHA256(salt + password), salt = 8 octets, 1000 itérations."""
    salt = raw[:LEGACY_SALT_SIZE]
    digest = raw[LEGACY_SALT_SIZE:]
    salt_b64 = base64.b64encode(salt).decode().rstrip("=")
    hash_b64 = base64.b64encode(digest).decode().rstrip("=")
    return f"$dynamic_82${hash_b64}${salt_b64}"


def convert_modern(raw: bytes) -> str:
    """Format moderne : PBKDF2WithHmacSHA256, 600000 itérations, salt = 8 octets."""
    salt = raw[:MODERN_SALT_SIZE]
    digest = raw[MODERN_SALT_SIZE:]
    salt_b64 = base64.b64encode(salt).decode().rstrip("=")
    hash_b64 = base64.b64encode(digest).decode().rstrip("=")
    return f"${MODERN_ALGO}${MODERN_ITERATIONS}${salt_b64}${hash_b64}"


def convert_hash(encoded: str, force_legacy: bool = False):
    """Convertit un hash Mirth unique vers le format John."""
    raw = decode_base64_hash(encoded)
    if raw is None:
        return None

    if force_legacy:
        return convert_legacy(raw)

    htype = detect_hash_type(raw)
    if htype == "modern":
        return convert_modern(raw)
    elif htype == "legacy":
        return convert_legacy(raw)
    else:
        return None


# ------------------------------
# Interface en ligne de commande
# ------------------------------
def main():
    parser = argparse.ArgumentParser(
        prog="mirth2john",
        description="Convertit les hashes Mirth Connect vers John the Ripper.",
        add_help=False   # désactive -h pour --help, on le récupère pour --hash
    )

    parser.add_argument(
        "-h", "--hash", dest="hash", metavar="HASH",
        help="Hash Base64 unique à convertir (affiché sur stdout)."
    )
    parser.add_argument(
        "-f", "--file", dest="infile", metavar="FILE",
        help="Fichier d'entrée avec un hash par ligne."
    )
    parser.add_argument(
        "-o", "--output", dest="outfile", metavar="FILE",
        help="Fichier de sortie (nécessite -f)."
    )
    parser.add_argument(
        "--legacy", action="store_true",
        help="Forcer le format legacy SHA256/1000."
    )
    parser.add_argument(
        "--help", action="help",
        help="Afficher ce message d'aide et quitter."
    )

    args = parser.parse_args()

    if not args.hash and not args.infile:
        parser.print_help()
        sys.exit(1)

    # Mode hash unique
    if args.hash:
        result = convert_hash(args.hash, force_legacy=args.legacy)
        if result:
            print(result)
        else:
            print("[-] Échec de l'analyse du hash.", file=sys.stderr)
            sys.exit(1)

    # Mode fichier
    if args.infile:
        if not args.outfile:
            print("[-] -o est obligatoire avec -f.", file=sys.stderr)
            sys.exit(1)

        converted = []
        try:
            with open(args.infile, "r") as f:
                for lineno, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    res = convert_hash(line, force_legacy=args.legacy)
                    if res:
                        converted.append(res)
                    else:
                        print(f"[-] Ligne {lineno} : échec de l'analyse.", file=sys.stderr)
        except FileNotFoundError:
            print(f"[-] Fichier introuvable : {args.infile}", file=sys.stderr)
            sys.exit(1)

        with open(args.outfile, "w") as f:
            f.write("\n".join(converted) + "\n")
        print(f"[+] {len(converted)} hashes écrits dans {args.outfile}")


if __name__ == "__main__":
    main()