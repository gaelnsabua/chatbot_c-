# Création du modèle SQUAD-CSHARP

## Prérequis
- Ollama installé et démarré (`ollama serve`)
- Le modèle de base téléchargé (`ollama pull llama3.2:3b`)

## Commandes

### Créer le modèle
```bash
cd models
ollama create SQUAD-CSHARP -f Modelfile
```

### Vérifier
```bash
ollama list
```

### Tester
```bash
ollama run SQUAD-CSHARP "Bonjour, qui es-tu ?"
```

### Supprimer et recréer
```bash
ollama rm SQUAD-CSHARP
ollama create SQUAD-CSHARP -f Modelfile
```
