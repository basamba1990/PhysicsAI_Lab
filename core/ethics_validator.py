"""
Ethics Validator - Module d'audit éthique pour les systèmes d'IA
Valide les décisions et outputs d'IA par rapport à des règles éthiques configurables.
"""

import json
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class EthicsValidator:
    """
    Module d'audit éthique pour les systèmes d'IA.
    Valide les décisions ou les outputs d'un modèle d'IA par rapport à des règles éthiques prédéfinies.
    Supporte les règles configurables et le logging des violations.
    """

    def __init__(self, rules_path: Optional[str] = None, custom_rules: Optional[List[Dict[str, Any]]] = None):
        """
        Initialise le validateur éthique.
        
        Args:
            rules_path: Chemin vers un fichier JSON de règles
            custom_rules: Liste de règles personnalisées
        """
        if rules_path:
            self.rules = self._load_rules(rules_path)
        elif custom_rules:
            self.rules = custom_rules
        else:
            self.rules = self._get_default_rules()
        
        self.violation_log = []
        logger.info(f"EthicsValidator initialisé avec {len(self.rules)} règles.")

    def _get_default_rules(self) -> List[Dict[str, Any]]:
        """Retourne les règles éthiques par défaut."""
        return [
            {
                "id": "bias_detection",
                "name": "Détection de biais discriminatoires",
                "description": "Détecte les biais discriminatoires dans les outputs de l'IA.",
                "criteria": {
                    "keywords": ["genre", "race", "âge", "religion", "origine", "handicap"],
                    "threshold": 0.7
                },
                "severity": "CRITICAL",
                "enabled": True
            },
            {
                "id": "transparency_check",
                "name": "Vérification de la transparence",
                "description": "Vérifie que les explications de l'IA sont suffisamment transparentes.",
                "criteria": {
                    "min_explanation_length": 50,
                    "required_terms": ["raison", "facteur", "impact", "justification"]
                },
                "severity": "HIGH",
                "enabled": True
            },
            {
                "id": "environmental_impact",
                "name": "Impact environnemental",
                "description": "Évalue l'impact environnemental des recommandations.",
                "criteria": {
                    "negative_keywords": ["carbone élevé", "déforestation", "pollution", "émissions"],
                    "positive_keywords": ["énergie verte", "recyclage", "durable", "efficacité énergétique"]
                },
                "severity": "MEDIUM",
                "enabled": True
            },
            {
                "id": "privacy_check",
                "name": "Vérification de la confidentialité",
                "description": "Vérifie que les données personnelles ne sont pas exposées.",
                "criteria": {
                    "sensitive_keywords": ["email", "téléphone", "adresse", "ssn", "numéro de compte"],
                    "threshold": 0.5
                },
                "severity": "CRITICAL",
                "enabled": True
            },
            {
                "id": "fairness_check",
                "name": "Vérification de l'équité",
                "description": "Vérifie que le modèle traite équitablement tous les groupes.",
                "criteria": {
                    "fairness_metrics": ["demographic_parity", "equal_opportunity", "calibration"],
                    "threshold": 0.8
                },
                "severity": "HIGH",
                "enabled": True
            },
            {
                "id": "uncertainty_communication",
                "name": "Communication de l'incertitude",
                "description": "Vérifie que l'incertitude des prédictions est communiquée.",
                "criteria": {
                    "required_fields": ["confidence", "uncertainty", "error_bounds"],
                    "min_confidence": 0.5
                },
                "severity": "MEDIUM",
                "enabled": True
            }
        ]

    def _load_rules(self, rules_path: str) -> List[Dict[str, Any]]:
        """Charge les règles éthiques à partir d'un fichier JSON."""
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            logger.info(f"Règles éthiques chargées depuis: {rules_path}")
            return rules
        except FileNotFoundError:
            logger.warning(f"Fichier de règles non trouvé: {rules_path}. Utilisation des règles par défaut.")
            return self._get_default_rules()
        except json.JSONDecodeError:
            logger.error(f"Erreur de décodage JSON dans: {rules_path}")
            return self._get_default_rules()

    def validate(
        self, 
        ai_output: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Valide un output d'IA par rapport aux règles éthiques.
        
        Args:
            ai_output: Dictionnaire contenant l'output de l'IA
            context: Contexte additionnel (ex: user_id, model_version)
            
        Returns:
            Dictionnaire avec violations et score d'éthique
        """
        violations = []
        output_text = str(ai_output.get("text", "")).lower()
        output_decision = str(ai_output.get("decision", ""))
        confidence = float(ai_output.get("confidence", 0.0))
        uncertainty = ai_output.get("uncertainty", None)
        
        # Évaluation de chaque règle
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            
            rule_violations = self._check_rule(rule, ai_output, output_text, output_decision, confidence, uncertainty)
            violations.extend(rule_violations)
        
        # Calcul du score d'éthique
        ethics_score = self._calculate_ethics_score(violations)
        
        # Logging des violations
        if violations:
            self._log_violations(violations, context)
        
        return {
            "violations": violations,
            "ethics_score": ethics_score,
            "is_ethical": len([v for v in violations if v["severity"] == "CRITICAL"]) == 0,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }

    def _check_rule(
        self,
        rule: Dict[str, Any],
        ai_output: Dict[str, Any],
        output_text: str,
        output_decision: str,
        confidence: float,
        uncertainty: Optional[Any]
    ) -> List[Dict[str, Any]]:
        """Vérifie une règle spécifique."""
        violations = []
        rule_id = rule["id"]
        
        if rule_id == "bias_detection":
            for keyword in rule["criteria"].get("keywords", []):
                if keyword in output_text:
                    violations.append({
                        "rule_id": rule_id,
                        "rule_name": rule.get("name", rule_id),
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "details": f"Mot-clé potentiellement biaisé détecté: '{keyword}'",
                        "detected_at": datetime.now().isoformat()
                    })
        
        elif rule_id == "transparency_check":
            min_length = rule["criteria"].get("min_explanation_length", 50)
            required_terms = rule["criteria"].get("required_terms", [])
            
            if len(output_text) < min_length or not all(term in output_text for term in required_terms):
                violations.append({
                    "rule_id": rule_id,
                    "rule_name": rule.get("name", rule_id),
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "details": "Explication insuffisante ou non transparente.",
                    "detected_at": datetime.now().isoformat()
                })
        
        elif rule_id == "environmental_impact":
            negative_keywords = rule["criteria"].get("negative_keywords", [])
            positive_keywords = rule["criteria"].get("positive_keywords", [])
            
            has_negative = any(kw in output_text for kw in negative_keywords)
            has_positive = any(kw in output_text for kw in positive_keywords)
            
            if has_negative and not has_positive:
                violations.append({
                    "rule_id": rule_id,
                    "rule_name": rule.get("name", rule_id),
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "details": "Recommandation avec impact environnemental négatif détecté.",
                    "detected_at": datetime.now().isoformat()
                })
        
        elif rule_id == "privacy_check":
            sensitive_keywords = rule["criteria"].get("sensitive_keywords", [])
            for keyword in sensitive_keywords:
                if keyword in output_text:
                    violations.append({
                        "rule_id": rule_id,
                        "rule_name": rule.get("name", rule_id),
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "details": f"Donnée sensible potentiellement exposée: '{keyword}'",
                        "detected_at": datetime.now().isoformat()
                    })
        
        elif rule_id == "fairness_check":
            # Vérification basique de l'équité (peut être étendue)
            if confidence < rule["criteria"].get("threshold", 0.8):
                violations.append({
                    "rule_id": rule_id,
                    "rule_name": rule.get("name", rule_id),
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "details": f"Confiance insuffisante pour garantir l'équité: {confidence:.2f}",
                    "detected_at": datetime.now().isoformat()
                })
        
        elif rule_id == "uncertainty_communication":
            required_fields = rule["criteria"].get("required_fields", [])
            missing_fields = [f for f in required_fields if f not in ai_output]
            
            if missing_fields:
                violations.append({
                    "rule_id": rule_id,
                    "rule_name": rule.get("name", rule_id),
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "details": f"Champs d'incertitude manquants: {', '.join(missing_fields)}",
                    "detected_at": datetime.now().isoformat()
                })
        
        return violations

    def _calculate_ethics_score(self, violations: List[Dict[str, Any]]) -> float:
        """Calcule un score d'éthique global (0-1)."""
        if not violations:
            return 1.0
        
        severity_weights = {
            "CRITICAL": 0.5,
            "HIGH": 0.3,
            "MEDIUM": 0.15,
            "LOW": 0.05
        }
        
        total_penalty = sum(severity_weights.get(v["severity"], 0.1) for v in violations)
        ethics_score = max(0.0, 1.0 - total_penalty)
        
        return ethics_score

    def _log_violations(self, violations: List[Dict[str, Any]], context: Optional[Dict[str, Any]]):
        """Enregistre les violations pour audit."""
        violation_record = {
            "timestamp": datetime.now().isoformat(),
            "violations": violations,
            "context": context or {},
            "hash": hashlib.sha256(json.dumps(violations, sort_keys=True).encode()).hexdigest()
        }
        self.violation_log.append(violation_record)
        
        logger.warning(f"Violations éthiques détectées: {len(violations)}")

    def add_rule(self, rule: Dict[str, Any]):
        """Ajoute une nouvelle règle éthique dynamiquement."""
        if "id" not in rule:
            raise ValueError("Rule must have an 'id' field")
        
        # Vérifier que l'ID est unique
        if any(r["id"] == rule["id"] for r in self.rules):
            logger.warning(f"Règle avec ID '{rule['id']}' existe déjà. Remplacement.")
            self.rules = [r for r in self.rules if r["id"] != rule["id"]]
        
        self.rules.append(rule)
        logger.info(f"Règle éthique ajoutée: {rule.get('id', 'N/A')}")

    def remove_rule(self, rule_id: str):
        """Supprime une règle éthique par son ID."""
        self.rules = [rule for rule in self.rules if rule.get("id") != rule_id]
        logger.info(f"Règle éthique supprimée: {rule_id}")

    def enable_rule(self, rule_id: str):
        """Active une règle éthique."""
        for rule in self.rules:
            if rule.get("id") == rule_id:
                rule["enabled"] = True
                logger.info(f"Règle activée: {rule_id}")
                return
        logger.warning(f"Règle non trouvée: {rule_id}")

    def disable_rule(self, rule_id: str):
        """Désactive une règle éthique."""
        for rule in self.rules:
            if rule.get("id") == rule_id:
                rule["enabled"] = False
                logger.info(f"Règle désactivée: {rule_id}")
                return
        logger.warning(f"Règle non trouvée: {rule_id}")

    def get_violation_report(self) -> Dict[str, Any]:
        """Génère un rapport des violations."""
        return {
            "total_violations": len(self.violation_log),
            "violations": self.violation_log,
            "summary": {
                "critical": len([v for log in self.violation_log for v in log["violations"] if v["severity"] == "CRITICAL"]),
                "high": len([v for log in self.violation_log for v in log["violations"] if v["severity"] == "HIGH"]),
                "medium": len([v for log in self.violation_log for v in log["violations"] if v["severity"] == "MEDIUM"]),
                "low": len([v for log in self.violation_log for v in log["violations"] if v["severity"] == "LOW"])
            }
        }

    def save_rules(self, output_path: str):
        """Sauvegarde les règles actuelles en JSON."""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Règles sauvegardées: {output_path}")


if __name__ == "__main__":
    validator = EthicsValidator()

    # Test 1: Output biaisé
    ai_output_biased = {
        "text": "Le candidat masculin est le plus qualifié pour ce poste de direction.",
        "decision": "embauche",
        "confidence": 0.95
    }
    result = validator.validate(ai_output_biased, context={"test": "bias_detection"})
    print("\n--- Test Output Biaisé ---")
    print(f"Violations: {len(result['violations'])}")
    print(f"Ethics Score: {result['ethics_score']:.2f}")
    print(f"Is Ethical: {result['is_ethical']}")

    # Test 2: Output transparent
    ai_output_transparent = {
        "text": "La décision est basée sur les facteurs X, Y et Z. La raison principale est la performance historique. L'impact estimé est positif.",
        "decision": "approbation",
        "confidence": 0.85,
        "uncertainty": 0.15
    }
    result = validator.validate(ai_output_transparent, context={"test": "transparency_check"})
    print("\n--- Test Output Transparent ---")
    print(f"Violations: {len(result['violations'])}")
    print(f"Ethics Score: {result['ethics_score']:.2f}")
    print(f"Is Ethical: {result['is_ethical']}")

    # Test 3: Rapport de violations
    print("\n--- Rapport de Violations ---")
    report = validator.get_violation_report()
    print(f"Total violations: {report['total_violations']}")
    print(f"Summary: {report['summary']}")
