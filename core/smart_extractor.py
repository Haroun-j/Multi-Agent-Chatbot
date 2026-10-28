"""
EXTRACTEUR DE DONNÉES INTELLIGENT
==================================

Extrait intelligemment les données des messages sans format rigide:
- Références clients (13 chiffres)
- Numéros de commande (CMD-XXXX-XXXX)
- Numéros de facture (FACT-XXXX-XXXX)
- Numéros de tracking (TRACK-XX-XXXXXXXXX)
- Emails
- Noms et prénoms
- Dates
- Montants
"""

import re
from datetime import datetime, timedelta
import database_mysql as db

class SmartExtractor:
    """Extracteur intelligent de données depuis texte libre"""
    
    @staticmethod
    def extract_client_reference(text):
        """Extrait référence client (13 chiffres)"""
        # Patterns: "1234567890123", "ref 1234567890123", "référence: 1234567890123"
        match = re.search(r'\b(\d{13})\b', text)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_order_number(text):
        """Extrait numéro de commande CMD-YYYY-NNNN"""
        match = re.search(r'\b(CMD-\d{4}-\d{4})\b', text, re.IGNORECASE)
        return match.group(1).upper() if match else None
    
    @staticmethod
    def extract_invoice_number(text):
        """Extrait numéro de facture FACT-YYYY-NNNN"""
        match = re.search(r'\b(FACT-\d{4}-\d{4})\b', text, re.IGNORECASE)
        return match.group(1).upper() if match else None
    
    @staticmethod
    def extract_tracking_number(text):
        """Extrait numéro de tracking TRACK-XX-XXXXXXXXX"""
        match = re.search(r'\b(TRACK-[A-Z]{2}-\d{9})\b', text, re.IGNORECASE)
        return match.group(1).upper() if match else None
    
    @staticmethod
    def extract_email(text):
        """Extrait email"""
        match = re.search(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', text)
        return match.group(1).lower() if match else None
    
    @staticmethod
    def extract_name(text, context_expects_name=False):
        """
        Extrait nom et prénom UNIQUEMENT si le contexte l'indique
        
        Args:
            text: Le texte à analyser
            context_expects_name: Si True, le système attend explicitement un nom
        
        Returns: (prénom, nom) ou None
        """
        # NE PAS extraire de nom si on n'attend pas explicitement un nom
        if not context_expects_name:
            # Patterns de présentation explicite seulement
            text_lower = text.lower()
            explicit_patterns = [
                r"(?:je m'appelle|je suis|mon nom est|nom:?)\s+([a-zàâäéèêëïîôùûü]+)\s+([a-zàâäéèêëïîôùûü]+)",
            ]
            
            for pattern in explicit_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    return (match.group(1).capitalize(), match.group(2).capitalize())
            
            return None
        
        # Si on attend explicitement un nom
        text_lower = text.lower()
        
        # Patterns de présentation
        patterns = [
            r"(?:je m'appelle|je suis|mon nom est|c'est)\s+([a-zàâäéèêëïîôùûü]+)\s+([a-zàâäéèêëïîôùûü]+)",
            r"^([a-zàâäéèêëïîôùûü\-]+)\s+([a-zàâäéèêëïîôùûü\-]+)$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return (match.group(1).capitalize(), match.group(2).capitalize())
        
        # Deux mots consécutifs (minimum 2 lettres chacun)
        # Mais seulement si le texte est court (pas une phrase)
        words = text_lower.strip().split()
        if len(words) == 2 or len(words) == 3: # "Alice Martin" ou "Alice de Martin"
            # Exclure mots communs
            excluded = {'mon', 'ton', 'son', 'mes', 'tes', 'ses', 'bonjour', 'salut', 
                       'merci', 'suis', 'appelle', 'nom', 'prenom', 'prénom', 'de', 'la', 'le'}
            
            # Filtrer et prendre premier et dernier mot
            filtered = [w for w in words if w not in excluded and len(w) >= 2]
            if len(filtered) >= 2:
                return (filtered[0].capitalize(), filtered[-1].capitalize())
        
        return None
    
    @staticmethod
    def extract_date(text):
        """
        Extrait une date du texte
        Supporte: "01/01/2026", "janvier", "hier", "avant-hier", etc.
        """
        # Date au format DD/MM/YYYY ou DD-MM-YYYY
        match = re.search(r'\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b', text)
        if match:
            try:
                return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            except:
                pass
        
        # Dates relatives
        text_lower = text.lower()
        today = datetime.now()
        
        if 'hier' in text_lower:
            return today - timedelta(days=1)
        if 'avant-hier' in text_lower or 'avant hier' in text_lower:
            return today - timedelta(days=2)
        if 'semaine dernière' in text_lower or 'semaine derniere' in text_lower:
            return today - timedelta(days=7)
        
        # Mois
        mois = {
            'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
        }
        
        for mois_nom, mois_num in mois.items():
            if mois_nom in text_lower:
                return datetime(today.year, mois_num, 1)
        
        return None
    
    @staticmethod
    def extract_amount(text):
        """Extrait un montant en euros"""
        # Patterns: "50€", "50 euros", "50.99€"
        patterns = [
            r'(\d+(?:[.,]\d{2})?)\s*(?:€|euros?|eur)',
            r'(\d+(?:[.,]\d{2})?)\s*e\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    return float(amount_str)
                except:
                    pass
        
        return None
    
    @staticmethod
    def extract_all(text, awaiting_name=False):
        """
        Extrait toutes les données possibles d'un texte
        
        Args:
            text: Texte à analyser
            awaiting_name: Si True, le système attend explicitement un nom
            
        Returns: dict avec toutes les données trouvées
        """
        return {
            'client_reference': SmartExtractor.extract_client_reference(text),
            'order_number': SmartExtractor.extract_order_number(text),
            'invoice_number': SmartExtractor.extract_invoice_number(text),
            'tracking_number': SmartExtractor.extract_tracking_number(text),
            'email': SmartExtractor.extract_email(text),
            'name': SmartExtractor.extract_name(text, context_expects_name=awaiting_name),
            'date': SmartExtractor.extract_date(text),
            'amount': SmartExtractor.extract_amount(text),
        }
    
    @staticmethod
    def find_order_flexible(text, client_id=None):
        """
        Recherche flexible de commande
        - Par numéro de commande
        - Par produit mentionné
        - Par date
        - "dernière commande", "avant-dernière"
        """
        # Extraire numéro de commande explicite
        order_num = SmartExtractor.extract_order_number(text)
        if order_num:
            query = "SELECT * FROM commandes WHERE order_number = %s"
            results = db.execute_query(query, (order_num,))
            return results[0] if results else None
        
        # Si client identifié, chercher par contexte
        if not client_id:
            return None
        
        text_lower = text.lower()
        
        # "Dernière commande"
        if any(w in text_lower for w in ['dernière', 'derniere', 'récente', 'recente']):
            query = """
                SELECT * FROM commandes 
                WHERE client_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            results = db.execute_query(query, (client_id,))
            return results[0] if results else None
        
        # "Avant-dernière" ou "celle d'avant"
        if any(w in text_lower for w in ['avant', 'précédente', 'precedente']):
            query = """
                SELECT * FROM commandes 
                WHERE client_id = %s 
                ORDER BY created_at DESC 
                LIMIT 2
            """
            results = db.execute_query(query, (client_id,))
            return results[1] if results and len(results) > 1 else None
        
        # Recherche par produit mentionné (iPhone, MacBook, etc.)
        products_keywords = {
            'iphone': 'iPhone',
            'macbook': 'MacBook',
            'samsung': 'Samsung',
            'playstation': 'PlayStation',
            'xbox': 'Xbox',
            'switch': 'Switch'
        }
        
        for keyword, product_name in products_keywords.items():
            if keyword in text_lower:
                query = """
                    SELECT DISTINCT c.* 
                    FROM commandes c
                    JOIN commande_items ci ON c.id = ci.commande_id
                    JOIN produits p ON ci.produit_id = p.id
                    WHERE c.client_id = %s 
                    AND p.name LIKE %s
                    ORDER BY c.created_at DESC
                    LIMIT 1
                """
                results = db.execute_query(query, (client_id, f'%{product_name}%'))
                if results:
                    return results[0]
        
        return None

# Fonction utilitaire globale
def extract_data_smart(text, awaiting_name=False):
    """Fonction helper pour extraction rapide"""
    return SmartExtractor.extract_all(text, awaiting_name=awaiting_name)
