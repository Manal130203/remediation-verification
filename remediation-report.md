# Rapport de remédiation de sécurité — ArchiveKit



## 1. Résumé exécutif



Ce projet est un exercice de sécurité portant sur le contrôle d’accès aux fichiers téléchargés dans une application fictive appelée ArchiveKit.



L’objectif était d’identifier et de corriger des vulnérabilités de validation des chemins pouvant permettre à un utilisateur d’accéder à des fichiers situés en dehors du répertoire de son tenant.



La version originale présentait deux vulnérabilités confirmées dans la simulation :

- Une validation insuffisante des préfixes de chemin, permettant de confondre `exports/red/` avec un répertoire voisin tel que `exports/red-old/`.

- Une validation effectuée avant le décodage des caractères encodés, permettant de contourner le contrôle d’accès avec un chemin contenant une séquence de traversal encodée.



La version corrigée bloque les deux scénarios reproduits. Une suite de 17 tests automatisés vérifie les principaux comportements de sécurité et de régression.



**Périmètre :** cette validation concerne une simulation en mémoire et ne constitue pas une certification de sécurité d’un système de production.



## 2. Périmètre et environnement



Le projet utilise Python, le module standard `unittest` et une représentation simulée des fichiers à l’aide de `files.json`.



L’application de démonstration reçoit une requête contenant notamment :

- un identifiant de requête ;

- un tenant ;

- un chemin de fichier demandé.



Les réponses simulées utilisent les statuts suivants :

- `200` : fichier autorisé et présent ;

- `403` : chemin interdit ou requête non autorisée ;

- `404` : fichier absent dans le périmètre autorisé.



Les données sont fictives. L’exercice n’accède pas à un véritable système de fichiers de production et ne teste pas un serveur HTTP réel.



## 3. Vulnérabilités identifiées



### 3.1. Contournement par préfixe de chemin



**Description**



La version originale utilisait une vérification de préfixe qui ne garantissait pas une frontière stricte entre les répertoires.



Par exemple, le chemin `exports/red-old/staging.txt` commence par le texte `exports/red`, mais il ne se trouve pas dans le répertoire autorisé `exports/red/`.



**Impact potentiel**



Une vérification de préfixe insuffisante peut autoriser l’accès à un fichier appartenant à un répertoire voisin.



**Résultat de la simulation**

- Version originale : `200`

- Version corrigée : `403`



Le test correspondant est `test_sibling_prefix_is_denied`.



### 3.2. Contournement par traversal encodé



**Description**



La version originale effectuait son contrôle d’accès avant de décoder les caractères encodés dans le chemin.



Le scénario testé utilise le chemin `exports/red/%2e%2e/blue/q2.csv`. Après décodage, `%2e%2e` représente le segment `..`, qui permet de remonter dans l’arborescence virtuelle.



**Impact potentiel**



Un contrôle effectué dans le mauvais ordre peut autoriser l’accès à un fichier appartenant à un autre tenant.



**Résultat de la simulation**

- Version originale : `200`

- Version corrigée : `403`



Le test correspondant est `test_encoded_traversal_is_denied`.



## 4. Mesures correctives appliquées



La version corrigée de `download.py` met en œuvre plusieurs contrôles.



### 4.1. Décodage unique



Le chemin est décodé une seule fois à l’aide de `urllib.parse.unquote`.



Le code ne tente pas de décoder récursivement les séquences restantes.



### 4.2. Rejet des chemins dangereux



La validation rejette notamment :

- les chemins absolus ;

- les antislashs, y compris lorsqu’ils sont encodés ;

- les caractères de contrôle ;

- les tenants inconnus ;

- les chemins dont la normalisation sort du répertoire autorisé.



### 4.3. Normalisation et contrôle de la frontière du tenant



La fonction `posixpath.normpath` normalise les segments du chemin. Le code vérifie ensuite que le chemin normalisé reste strictement sous `exports/<tenant>/`.



Cette vérification empêche qu’un simple préfixe textuel, tel que `exports/red-old/`, soit considéré comme appartenant au tenant `red`.



### 4.4. Réponses contrôlées



Les requêtes interdites reçoivent une réponse `403` sans divulgation du contenu du fichier protégé.



Un fichier absent dans le périmètre autorisé reçoit une réponse `404`.



## 5. Tests automatisés reproductibles



La suite de tests se trouve dans `inputs/test_download.py`. Elle utilise `unittest`, inclus dans Python, sans nécessiter l’installation de `pytest`.



Les 17 tests couvrent notamment :



- les téléchargements légitimes des tenants `red` et `blue` ;

- les noms de fichiers contenant un espace encodé ;

- la normalisation des segments `.` ;

- les préfixes de répertoire voisins ;

- les tentatives d’accès à un autre tenant ;

- les chemins privés et les tenants inconnus ;

- les traversals encodés et les traversals multiples ;

- les chemins absolus et les antislashs ;

- le comportement face au double encodage ;

- les fichiers absents ;

- l’absence de divulgation du contenu des fichiers interdits.



Les assertions vérifient les statuts et les corps des réponses.



Le test `test_double_encoded_traversal_is_not_decoded_twice` vérifie spécifiquement qu’un chemin contenant un traversal doublement encodé ne permet pas de récupérer le fichier de l’autre tenant.



Les tests ne prouvent pas à eux seuls l’absence de toute vulnérabilité possible, mais fournissent une base reproductible pour détecter les régressions couvertes.



## 6. Résultats de vérification



La vérification a été exécutée avec le script PowerShell `verify.ps1`.



**Résultats observés :**

- 17 tests exécutés ;

- 17 tests réussis ;

- aucune régression détectée par cette suite ;

- les deux scénarios vulnérables ont été reproduits avec la version originale ;

- les deux scénarios sont bloqués par la version corrigée.



Pour les deux attaques comparées, la version originale retourne `200` et la version corrigée retourne `403`.



Le script se termine avec le message :



`ALL SECURITY CHECKS PASSED.`



Le rapport des tests automatisés est conservé dans `fixed-tests.txt`. Le script `verify.ps1` permet de répéter les vérifications.



## 7. Limites et recommandations



Cette réalisation est une simulation en mémoire. Elle ne valide pas le comportement d’un serveur HTTP réel ni celui d’un stockage de fichiers en production.



Avant tout déploiement réel, il serait nécessaire de réaliser des tests d’intégration couvrant notamment :

- le traitement réel des requêtes HTTP et le décodage des URL ;

- la cohérence de la canonicalisation entre les différentes couches de l’application ;

- les interactions avec le système de fichiers ou le stockage objet ;

- les liens symboliques et les particularités du système d’exploitation ;

- l’authentification et l’autorisation des tenants ;

- la journalisation, la gestion des erreurs et les réponses en cas d’échec.



Il est également recommandé de conserver les tests dans le dépôt et de les exécuter automatiquement à chaque modification du code.



## 8. Conclusion



L’exercice a permis d’identifier deux vulnérabilités de validation des chemins dans une implémentation fictive, de corriger les contrôles concernés et de mettre en place une suite de 17 tests automatisés.



Les vérifications réalisées montrent que les deux attaques ciblées sont bloquées par la version corrigée et que les tests de régression existants passent.



Le projet démontre une démarche structurée de remédiation : reproduction du problème, correction, tests automatisés, comparaison entre versions et conservation des résultats.



Les conclusions restent limitées au périmètre de la simulation et doivent être complétées par des tests d’intégration avant toute application à un système réel.
@'

## 9. Tests de sécurité adversariaux

Une suite complémentaire a été ajoutée dans `inputs/test_adversarial.py`.

Les 11 tests adversariaux ont réussi, sans échec (`OK`). Ils couvrent :
- les traversées de répertoires avec plusieurs segments `..` ;
- les points et slashs encodés ;
- le décodage du chemin exactement une fois ;
- les chemins absolus et les antislashs encodés ;
- les chemins légitimes contenant un segment `.` ou un espace ;
- les tentatives d'accès entre tenants et les préfixes similaires ;
- l'absence de contenu protégé dans les réponses `403`.

Les 17 tests de régression ont également réussi, sans échec (`OK`).

Les sorties sont conservées dans `adversarial-tests.txt` et `fixed-tests.txt`.
'@ | Add-Content -Encoding utf8 .\remediation-report.md

## 10. Exécution reproductible des vérifications

Le script `verify.ps1` exécute successivement :
- les 17 tests de régression ;
- les 11 tests de sécurité adversariaux ;
- la comparaison entre la version vulnérable et la version corrigée.

Le script s'arrête en cas d'échec et renvoie un code de sortie non nul.
Les résultats d'exécution sont enregistrés dans `verification-report.txt`.

Résultat : les vérifications exécutées ont réussi.
## 11. Séparation de la validation, de l'autorisation et de la recherche

Le traitement est organisé en étapes distinctes :
- validation du tenant et du chemin ;
- décodage du chemin une seule fois ;
- normalisation du chemin ;
- vérification de la frontière exacte du tenant ;
- recherche du fichier à partir de la clé validée ;
- construction d'une réponse contrôlée.

La fonction `_safe_key()` renvoie le chemin normalisé uniquement s'il respecte les règles d'accès. La fonction `download()` utilise ensuite cette même clé pour rechercher le contenu avec `files.get(key)`.

Les tests de régression et les tests adversariaux ont réussi lors de la vérification finale.
## 12. Mini-modèle de menace

### Actifs à protéger
Les actifs concernés sont les fichiers d’export et les données privées qu’ils contiennent. Leur divulgation à un tenant non autorisé peut compromettre la confidentialité des données et entraîner des conséquences métier ou réglementaires.

### Frontière de confiance
La frontière de confiance correspond à la séparation entre les tenants, notamment entre `exports/red/` et `exports/blue/`. Chaque tenant ne doit pouvoir accéder qu’aux fichiers relevant de son propre périmètre.

### Attaquant et scénario de menace
L’attaquant est un utilisateur autorisé à demander des téléchargements, mais qui tente de contourner les restrictions pour obtenir les fichiers d’un autre tenant. Il peut notamment manipuler le chemin demandé à l’aide de segments `..`, de séparateurs encodés ou de préfixes de répertoires similaires afin de contourner le contrôle d’accès.

### Impact potentiel
Une validation ou une autorisation incorrecte peut provoquer une divulgation de données privées, un accès inter-tenant non autorisé et un contournement du contrôle d’accès prévu par l’application.

### Mesures de réduction du risque
La correction applique une validation stricte du tenant et du chemin, décode le chemin une seule fois, normalise sa représentation, puis vérifie que le chemin normalisé reste dans le répertoire exact du tenant. La recherche du fichier utilise ensuite la même clé validée que celle ayant fait l’objet du contrôle d’autorisation. Les tests de régression et les tests adversariaux vérifient notamment les traversées de chemins, les préfixes trompeurs, les chemins encodés et l’absence de fuite de contenu dans les réponses de refus.

### Références OWASP
Les scénarios sont pertinents au regard des traversées de chemins (*Path Traversal*, CWE-22) et des défauts de contrôle d’accès (*Broken Access Control* dans l’OWASP Top 10). La correction vise à empêcher qu’un utilisateur autorisé à accéder à ses propres fichiers puisse accéder à ceux d’un autre tenant.

**Risque résiduel :** cette vérification porte sur la simulation et sa table de fichiers en mémoire. Une implémentation utilisant le système de fichiers réel devrait également vérifier les liens symboliques, la résolution effective des chemins et les permissions du système d’exploitation.


