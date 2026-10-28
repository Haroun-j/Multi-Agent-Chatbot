"""
FORM MANAGER - Gestionnaire de Formulaires Dynamiques
======================================================

Ce module gère la collecte progressive des données manquantes auprès de l'utilisateur.
Il génère des formulaires contextuels basés sur les besoins identifiés.

Fonctionnalités:
- Détection automatique des données manquantes
- Génération dynamique de formulaires
- Validation des entrées utilisateur
- Support multi-tours de conversation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


# ============================================================================
# DÉFINITION DES FORMULAIRES
# ============================================================================

FORM_TEMPLATES = {
    
    # Identification client - Formulaire de base
    "client_identification": {
        "name": "Identification Client",
        "description": "Formulaire pour identifier le client",
        "fields": [
            {
                "name": "client_reference",
                "type": "text",
                "required": True,
                "prompt": "Pour vous identifier, j'ai besoin de votre référence client (13 chiffres). Quelle est votre référence?",
                "validation": "client_reference",
                "error_message": "La référence client doit contenir exactement 13 chiffres."
            }
        ],
        "priority": 1  # Haute priorité - toujours demandé en premier
    },
    
    # Identification alternative par email
    "client_identification_email": {
        "name": "Identification par Email",
        "description": "Alternative: identifier le client par email",
        "fields": [
            {
                "name": "email",
                "type": "email",
                "required": True,
                "prompt": "Vous pouvez aussi vous identifier avec votre email. Quelle est votre adresse email?",
                "validation": "email",
                "error_message": "Veuillez entrer une adresse email valide."
            }
        ],
        "priority": 2  # Alternative à la référence
    },
    
    # Filtrage par dates
    "date_range_filter": {
        "name": "Filtre par Période",
        "description": "Demande une plage de dates pour filtrer les résultats",
        "fields": [
            {
                "name": "date_debut",
                "type": "date",
                "required": False,
                "prompt": "À partir de quelle date souhaitez-vous voir les résultats? (Format: JJ/MM/AAAA ou laissez vide pour toutes)",
                "validation": "date",
                "error_message": "Format de date invalide. Utilisez JJ/MM/AAAA (ex: 15/01/2026)"
            },
            {
                "name": "date_fin",
                "type": "date",
                "required": False,
                "prompt": "Jusqu'à quelle date? (Format: JJ/MM/AAAA ou laissez vide pour aujourd'hui)",
                "validation": "date",
                "error_message": "Format de date invalide. Utilisez JJ/MM/AAAA"
            }
        ],
        "priority": 3
    },
    
    # Recherche de commande spécifique
    "order_search": {
        "name": "Recherche de Commande",
        "description": "Rechercher une commande spécifique",
        "fields": [
            {
                "name": "order_number",
                "type": "text",
                "required": False,
                "prompt": "Avez-vous le numéro de commande? (Format: CMD-AAAA-XXXX)",
                "validation": "order_number",
                "error_message": "Le numéro de commande doit être au format CMD-AAAA-XXXX"
            },
            {
                "name": "approximate_date",
                "type": "date",
                "required": False,
                "prompt": "Si non, quand avez-vous passé la commande approximativement?",
                "validation": "date"
            }
        ],
        "priority": 2
    },
    
    # Suivi de livraison
    "delivery_tracking": {
        "name": "Suivi de Livraison",
        "description": "Suivre une livraison",
        "fields": [
            {
                "name": "tracking_number",
                "type": "text",
                "required": False,
                "prompt": "Avez-vous le numéro de suivi (tracking)?",
                "validation": "tracking",
                "error_message": "Format de numéro de tracking invalide"
            }
        ],
        "priority": 2
    },
    
    # Recherche de facture
    "invoice_search": {
        "name": "Recherche de Facture",
        "description": "Rechercher une facture",
        "fields": [
            {
                "name": "facture_number",
                "type": "text",
                "required": False,
                "prompt": "Avez-vous le numéro de facture? (Format: FACT-AAAA-XXXX)",
                "validation": "invoice_number"
            },
            {
                "name": "invoice_status",
                "type": "choice",
                "required": False,
                "prompt": "Quel type de factures? (toutes/impayées/payées)",
                "choices": ["toutes", "impayées", "payées"],
                "default": "toutes"
            }
        ],
        "priority": 2
    },
    
    # Recherche de produit
    "product_search": {
        "name": "Recherche de Produit",
        "description": "Rechercher des produits",
        "fields": [
            {
                "name": "search_term",
                "type": "text",
                "required": True,
                "prompt": "Que recherchez-vous? (nom, marque, ou description)",
                "validation": "non_empty"
            },
            {
                "name": "category",
                "type": "choice",
                "required": False,
                "prompt": "Dans quelle catégorie? (Smartphones/Ordinateurs/Audio/etc. ou laissez vide pour toutes)",
                "choices": ["Smartphones", "Ordinateurs", "Audio", "Photo & Vidéo", "Gaming", "Wearables", "Smart Home", "Accessoires"]
            },
            {
                "name": "max_price",
                "type": "number",
                "required": False,
                "prompt": "Prix maximum en euros?",
                "validation": "positive_number"
            }
        ],
        "priority": 2
    },
    
    # Validation de coupon
    "coupon_validation": {
        "name": "Validation de Coupon",
        "description": "Valider un code promo",
        "fields": [
            {
                "name": "coupon_code",
                "type": "text",
                "required": True,
                "prompt": "Quel est le code promo que vous souhaitez utiliser?",
                "validation": "coupon_code",
                "transform": "uppercase"
            }
        ],
        "priority": 2
    },
    
    # Demande de retour
    "return_request": {
        "name": "Demande de Retour",
        "description": "Initier une demande de retour",
        "fields": [
            {
                "name": "order_number",
                "type": "text",
                "required": True,
                "prompt": "Numéro de la commande concernée?",
                "validation": "order_number"
            },
            {
                "name": "product_name",
                "type": "text",
                "required": True,
                "prompt": "Quel produit souhaitez-vous retourner?",
                "validation": "non_empty"
            },
            {
                "name": "return_reason",
                "type": "choice",
                "required": True,
                "prompt": "Raison du retour?",
                "choices": ["défectueux", "mauvais article", "pas satisfait", "endommagé", "autre"]
            },
            {
                "name": "description",
                "type": "text",
                "required": False,
                "prompt": "Pouvez-vous décrire le problème en détail?"
            }
        ],
        "priority": 1
    }
}


# ============================================================================
# RÈGLES DE VALIDATION
# ============================================================================

VALIDATION_RULES = {
    "client_reference": lambda x: bool(re.match(r'^\d{13}$', str(x).strip())),
    "email": lambda x: bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(x).strip())),
    "date": lambda x: validate_date(x),
    "order_number": lambda x: bool(re.match(r'^CMD-\d{4}-\d{4}$', str(x).strip())),
    "invoice_number": lambda x: bool(re.match(r'^FACT-\d{4}-\d{4}$', str(x).strip())),
    "tracking": lambda x: len(str(x).strip()) > 5,  # Minimum 5 caractères
    "coupon_code": lambda x: len(str(x).strip()) >= 3,
    "non_empty": lambda x: len(str(x).strip()) > 0,
    "positive_number": lambda x: float(x) > 0 if x else True,
}


def validate_date(date_str):
    """Valide et parse une date au format JJ/MM/AAAA"""
    if not date_str or str(date_str).strip() == "":
        return True  # Les dates optionnelles peuvent être vides
    
    patterns = [
        r'^\d{2}/\d{2}/\d{4}$',  # JJ/MM/AAAA
        r'^\d{4}-\d{2}-\d{2}$',  # AAAA-MM-JJ
    ]
    
    date_str = str(date_str).strip()
    for pattern in patterns:
        if re.match(pattern, date_str):
            try:
                if '/' in date_str:
                    datetime.strptime(date_str, '%d/%m/%Y')
                else:
                    datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False
    return False


# ============================================================================
# TRANSFORMATIONS
# ============================================================================

TRANSFORMATIONS = {
    "uppercase": lambda x: str(x).upper(),
    "lowercase": lambda x: str(x).lower(),
    "strip": lambda x: str(x).strip(),
    "date_to_sql": lambda x: convert_date_to_sql(x),
}


def convert_date_to_sql(date_str):
    """Convertit JJ/MM/AAAA en AAAA-MM-JJ pour SQL"""
    if not date_str or str(date_str).strip() == "":
        return None
    
    date_str = str(date_str).strip()
    
    if '/' in date_str:
        try:
            dt = datetime.strptime(date_str, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    return date_str  # Déjà au bon format


# ============================================================================
# CLASSE FORM MANAGER
# ============================================================================

class FormManager:
    """Gère la création et la validation des formulaires"""
    
    def __init__(self):
        self.active_forms = {}  # {conversation_id: FormInstance}
    
    def get_form(self, form_name: str) -> Optional[Dict]:
        """
        Récupère un formulaire par son nom
        
        Args:
            form_name: Nom du formulaire
            
        Returns:
            dict: Template du formulaire ou None
        """
        return FORM_TEMPLATES.get(form_name)
    
    def create_form_instance(self, form_name: str, conversation_id: str) -> 'FormInstance':
        """
        Crée une instance de formulaire pour une conversation
        
        Args:
            form_name: Nom du formulaire
            conversation_id: ID de la conversation
            
        Returns:
            FormInstance: Instance du formulaire
        """
        template = self.get_form(form_name)
        if not template:
            raise ValueError(f"Formulaire '{form_name}' introuvable")
        
        instance = FormInstance(template, conversation_id)
        self.active_forms[conversation_id] = instance
        return instance
    
    def get_active_form(self, conversation_id: str) -> Optional['FormInstance']:
        """Récupère le formulaire actif pour une conversation"""
        return self.active_forms.get(conversation_id)
    
    def validate_field(self, field_def: Dict, value: Any) -> tuple[bool, Optional[str]]:
        """
        Valide un champ de formulaire
        
        Args:
            field_def: Définition du champ
            value: Valeur à valider
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Champ requis mais vide
        if field_def.get('required') and not value:
            return False, f"Le champ '{field_def['name']}' est requis"
        
        # Champ optionnel et vide - OK
        if not value and not field_def.get('required'):
            return True, None
        
        # Validation par règle
        validation_rule = field_def.get('validation')
        if validation_rule and validation_rule in VALIDATION_RULES:
            validator = VALIDATION_RULES[validation_rule]
            if not validator(value):
                return False, field_def.get('error_message', f"Valeur invalide pour '{field_def['name']}'")
        
        # Validation des choix
        if field_def.get('type') == 'choice' and field_def.get('choices'):
            if value not in field_def['choices']:
                return False, f"Choix invalide. Options: {', '.join(field_def['choices'])}"
        
        return True, None
    
    def transform_value(self, field_def: Dict, value: Any) -> Any:
        """Applique les transformations sur une valeur"""
        if not value:
            return value
        
        transform = field_def.get('transform')
        if transform and transform in TRANSFORMATIONS:
            return TRANSFORMATIONS[transform](value)
        
        # Transformation automatique des dates pour SQL
        if field_def.get('type') == 'date':
            return convert_date_to_sql(value)
        
        return value


class FormInstance:
    """Instance d'un formulaire pour une conversation spécifique"""
    
    def __init__(self, template: Dict, conversation_id: str):
        self.template = template
        self.conversation_id = conversation_id
        self.current_field_index = 0
        self.collected_data = {}
        self.completed = False
    
    def get_current_field(self) -> Optional[Dict]:
        """Récupère le champ actuel à remplir"""
        if self.current_field_index >= len(self.template['fields']):
            return None
        return self.template['fields'][self.current_field_index]
    
    def get_next_prompt(self) -> Optional[str]:
        """Récupère le prompt pour le prochain champ"""
        field = self.get_current_field()
        if not field:
            return None
        return field['prompt']
    
    def submit_field_value(self, value: Any, form_manager: FormManager) -> Dict:
        """
        Soumet une valeur pour le champ actuel
        
        Returns:
            dict: {
                'valid': bool,
                'error': str or None,
                'next_prompt': str or None,
                'completed': bool,
                'data': dict
            }
        """
        field = self.get_current_field()
        if not field:
            return {
                'valid': False,
                'error': "Formulaire déjà complété",
                'completed': True,
                'data': self.collected_data
            }
        
        # Validation
        is_valid, error = form_manager.validate_field(field, value)
        if not is_valid:
            return {
                'valid': False,
                'error': error,
                'next_prompt': field['prompt'],  # Redemander
                'completed': False,
                'data': self.collected_data
            }
        
        # Transformation
        transformed_value = form_manager.transform_value(field, value)
        
        # Sauvegarde
        self.collected_data[field['name']] = transformed_value
        self.current_field_index += 1
        
        # Vérifier si terminé
        next_field = self.get_current_field()
        if not next_field:
            self.completed = True
            return {
                'valid': True,
                'error': None,
                'next_prompt': None,
                'completed': True,
                'data': self.collected_data
            }
        
        # Prochain champ
        return {
            'valid': True,
            'error': None,
            'next_prompt': next_field['prompt'],
            'completed': False,
            'data': self.collected_data
        }
    
    def get_progress(self) -> str:
        """Retourne une chaîne de progression"""
        total = len(self.template['fields'])
        current = self.current_field_index
        return f"[{current}/{total}]"
    
    def is_completed(self) -> bool:
        """Vérifie si le formulaire est complété"""
        return self.completed


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def detect_missing_params(required_params: List[str], available_data: Dict) -> List[str]:
    """
    Détecte les paramètres manquants
    
    Args:
        required_params: Liste des paramètres requis
        available_data: Données disponibles
        
    Returns:
        list: Paramètres manquants
    """
    missing = []
    for param in required_params:
        if param not in available_data or available_data[param] is None:
            missing.append(param)
    return missing


def suggest_form_for_intent(intent: str, missing_params: List[str]) -> Optional[str]:
    """
    Suggère un formulaire basé sur l'intention et les paramètres manquants
    
    Args:
        intent: Intention détectée
        missing_params: Paramètres manquants
        
    Returns:
        str: Nom du formulaire suggéré ou None
    """
    # Mapping intention -> formulaire
    intent_form_mapping = {
        "check_order_status": "order_search",
        "track_delivery": "delivery_tracking",
        "view_invoices": "invoice_search",
        "product_search": "product_search",
        "validate_coupon": "coupon_validation",
        "return_product": "return_request",
    }
    
    # Si client_reference manquant, toujours demander identification d'abord
    if "client_reference" in missing_params and "client_id" in missing_params:
        return "client_identification"
    
    # Sinon, utiliser le mapping
    return intent_form_mapping.get(intent)


def list_all_forms() -> List[str]:
    """Liste tous les formulaires disponibles"""
    return list(FORM_TEMPLATES.keys())
