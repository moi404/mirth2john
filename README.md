# mirth2john

> Convertisseur de hashes **Mirth Connect** vers le format **John the Ripper**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 📖 Description

`mirth2john` est un outil en ligne de commande qui convertit les hashes de mots de passe stockés par **Mirth Connect** (moteur d'intégration de santé open source développé par NextGen Healthcare) vers un format directement exploitable par **John the Ripper** ou **Hashcat**.

L'outil supporte **automatiquement** les deux formats utilisés par Mirth Connect selon la version :

| Version Mirth | Algorithme | Itérations | Taille hash |
|---------------|------------|------------|-------------|
| ≤ 4.3.x       | SHA256 (salé) | 1 000  | 40 octets |
| ≥ 4.4.0       | PBKDF2-HMAC-SHA256 | 600 000 | 40 octets |

---

## ⚙️ Installation

### Prérequis

- Python 3.8 ou supérieur

### Installation rapide

```bash
git clone https://github.com/moi404/mirth2john.git
cd mirth2john
chmod +x mirth2john.py
sudo cp mirth2john.py /usr/local/bin/mirth2john
```

---

## 🚀 Utilisation

### 📋 Aide intégrée

```bash
mirth2john --help
```

**Sortie :**
```
usage: mirth2john [-h HASH] [-f FILE] [-o FILE] [--legacy] [--help]

Convertit les hashes Mirth Connect vers John the Ripper.

options:
  -h HASH, --hash HASH   Hash Base64 unique à convertir
  -f FILE, --file FILE   Fichier d'entrée avec un hash par ligne
  -o FILE, --output FILE Fichier de sortie (nécessite -f)
  --legacy               Force le format legacy SHA256/1000
  --help                 Affiche ce message d'aide et quitte
```

---

### 🔑 Commande 1 — Hash unique

Convertit un seul hash et l'affiche directement sur le terminal.

```bash
mirth2john -h 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w=='
```

**Sortie :**
```
$pbkdf2-sha256$600000$u/+LBBOUnac=$YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=
```

**Avec l'option longue (équivalente) :**
```bash
mirth2john --hash 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w=='
```

---

### 📦 Commande 2 — Conversion par lot

Convertit un fichier contenant plusieurs hashes (un par ligne).

**Fichier d'entrée `hashes.txt` :**
```
u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w==
dGhpcyBpcyBhIGZha2UgaGFzaCBmb3IgdGhlIGV4YW1wbGU=
# commentaire ignoré
```

```bash
mirth2john -f hashes.txt -o john_hashes.txt
```

**Fichier de sortie `john_hashes.txt` :**
```
$pbkdf2-sha256$600000$u/+LBBOUnac=$YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=
$dynamic_82$...$...
```

**Sortie terminal :**
```
[+] 2 hashes écrits dans john_hashes.txt
```

**Avec options longues :**
```bash
mirth2john --file hashes.txt --output john_hashes.txt
```

---

### 🔄 Commande 3 — Forcer le format legacy

Utilise ce flag si tu sais que la cible tourne sur **Mirth ≤ 4.3** (SHA256 / 1000 itérations).

**Hash unique :**
```bash
mirth2john --legacy -h 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w=='
```

**Conversion par lot :**
```bash
mirth2john --legacy -f hashes.txt -o john_hashes.txt
```

**Sortie :**
```
$dynamic_82$YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=$u/+LBBOUnac=
```

---

### 📝 Commande 4 — Format d'entrée avancé (avec username)

Le format accepté est `username:hash` ou simplement `hash`. Le username est **optionnel**.

**Fichier `hashes.txt` avec usernames :**
```
sedric:u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w==
admin:dGhpcyBpcyBhIGZha2UgaGFzaCBmb3IgdGhlIGV4YW1wbGU=
```

```bash
mirth2john -f hashes.txt -o john_hashes.txt
```

**Résultat :**
```
sedric:$pbkdf2-sha256$600000$u/+LBBOUnac=$YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=
admin:$pbkdf2-sha256$600000$dGhpcyBpcyBhIGZha2UgaGFzaCBmb3IgdGhlIGV4YW1wbGU=
```

---

## 📋 Tableau récapitulatif des options

| Option courte | Option longue | Argument | Description | Obligatoire |
|---------------|---------------|----------|-------------|-------------|
| `-h` | `--hash` | `<HASH>` | Hash Base64 unique à convertir | ⚠️ (ou `-f`) |
| `-f` | `--file` | `<FILE>` | Fichier d'entrée avec un hash par ligne | ⚠️ (ou `-h`) |
| `-o` | `--output` | `<FILE>` | Fichier de sortie (obligatoire avec `-f`) | ✅ avec `-f` |
| — | `--legacy` | — | Force le format legacy SHA256/1000 | ❌ |
| — | `--help` | — | Affiche l'aide | ❌ |

---

## 🔨 Craquage avec John the Ripper

Une fois convertis, les hashes peuvent être craqués directement :

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt john_hashes.txt
```

**Avec format explicite :**
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --format=pbkdf2-sha256 john_hashes.txt
```

**Afficher les mots de passe trouvés :**
```bash
john --show john_hashes.txt
```

**Exemple de sortie :**
```
sedric:snowflake1
```

---

## 🎯 Craquage avec Hashcat

Pour Hashcat, il faut un format différent. Convertis manuellement :

```bash
python3 -c "
import base64
h = 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w=='
d = base64.b64decode(h)
salt = base64.b64encode(d[:8]).decode().rstrip('=')
digest = base64.b64encode(d[8:]).decode().rstrip('=')
print(f'sha256:600000:{salt}:{digest}')
"
```

**Puis avec Hashcat :**
```bash
hashcat -m 10900 hash.txt /usr/share/wordlists/rockyou.txt
```

**Mode 10900** = PBKDF2-HMAC-SHA256 (600 000 itérations).

---

## 🧠 Comment ça marche

Mirth Connect stocke les mots de passe en **Base64(salt + hash)** où :
- **salt** = 8 premiers octets
- **hash** = 32 octets restants (SHA256 ou PBKDF2-HMAC-SHA256)

L'outil :
1. Décode la chaîne Base64
2. Sépare le sel (8 octets) du hash (32 octets)
3. Ré-encode chaque partie en Base64
4. Génère la ligne au format John the Ripper

---

## 🐛 Limitations connues

- **Ambiguïté legacy/moderne** : les deux formats produisent 40 octets après décodage. L'outil suppose **moderne par défaut** ; utilise `--legacy` si tu sais que la cible est Mirth ≤ 4.3.
- **Argon2** : Mirth supporte Argon2 mais il n'est pas activé par défaut. Non supporté pour l'instant.
- **Fallback Mirth 4.4** : lors de la migration 4.3 → 4.4, les anciens hashes sont conservés en SHA256/1000. Détecte-les manuellement.

---

## 🧪 Tests

**Test 1 — Hash unique (moderne) :**
```bash
python3 mirth2john.py -h 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w=='
```
**Attendu :**
```
$pbkdf2-sha256$600000$u/+LBBOUnac=$YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=
```

**Test 2 — Hash unique (legacy) :**
```bash
python3 mirth2john.py --legacy -h 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w=='
```
**Attendu :**
```
$dynamic_82$YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=$u/+LBBOUnac=
```

**Test 3 — Conversion par lot :**
```bash
echo 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w==' > test.txt
python3 mirth2john.py -f test.txt -o out.txt
cat out.txt
```

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Crée une branche (`git checkout -b feature/amelioration`)
3. Commit tes changements (`git commit -m 'Ajout fonctionnalité X'`)
4. Push sur la branche (`git push origin feature/amelioration`)
5. Ouvre une Pull Request

---

## ⚠️ Avertissement légal

Cet outil est destiné **exclusivement** à :
- Des tests d'intrusion **autorisés** par écrit
- Des environnements de **CTF** légitimes
- De la **recherche en sécurité** sur tes propres systèmes

L'utilisation sur des systèmes sans autorisation explicite est **illégale** et contraire à l'éthique. Les auteurs ne sont pas responsables d'un usage abusif.

---

## 📜 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [NextGen Healthcare](https://www.nextgen.com/) pour Mirth Connect
- [John the Ripper](https://www.openwall.com/john/) pour l'outil de craquage
- [HackTheBox](https://www.hackthebox.com/) pour la box *Interpreter* qui a inspiré cet outil

---

## 📬 Contact

- **Auteur** : moi404
- **GitHub** : [@moi404](https://github.com/moi404)

---

⭐ Si ce projet t'a aidé, n'hésite pas à lui mettre une étoile !
