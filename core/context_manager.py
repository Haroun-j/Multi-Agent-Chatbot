"""
CONTEXT MANAGER - Gestionnaire de Contexte Conversationnel
===========================================================

Ce module gère l'état et le contexte des conversations multi-tours.
Il maintient l'historique, les données collectées, et l'état des formulaires.

Fonctionnalités:
- Historique de conversation
- Persistance des données collectées
- Gestion des formulaires actifs
- Détection des intentions répétées
- Cache des requêtes récentes
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import json


class ConversationContext:
    """Gère le contexte d'une conversation unique"""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Historique des messages
        self.history = deque(maxlen=50)  # Garde les 50 derniers messages
        
        # Données collectées durant la conversation
        self.collected_data = {}
        
        # Client identifié (si applicable)
        self.client_info = None
        
        # Formulaire actif
        self.active_form = None
        self.form_data = {}
        
        # Agent actuel gérant la requête
        self.current_agent = None
        self.agent_history = []  # Historique des agents utilisés
        
        # Intentions détectées
        self.intent_history = []
        self.current_intent = None
        
        # Cache des requêtes DB récentes
        self.query_cache = {}
        self.cache_ttl = timedelta(minutes=5)  # TTL de 5 minutes
        
        # État de la conversation
        self.state = "active"  # active, waiting_input, completed, error
        
        # Méta-données
        self.metadata = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Ajoute un message à l'historique
        
        Args:
            role: 'user' ou 'assistant'
            content: Contenu du message
            metadata: Métadonnées additionnelles
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.history.append(message)
        self.last_activity = datetime.now()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Récupère l'historique des messages
        
        Args:
            limit: Nombre de messages à retourner (None = tous)
            
        Returns:
            list: Liste des messages
        """
        if limit:
            return list(self.history)[-limit:]
        return list(self.history)
    
    def set_client_info(self, client_data: Dict):
        """Enregistre les informations du client identifié"""
        self.client_info = client_data
        self.collected_data['client_id'] = client_data.get('id')
        self.collected_data['client_reference'] = client_data.get('client_reference')
        self.collected_data['email'] = client_data.get('email')
    
    def get_client_id(self) -> Optional[int]:
        """Récupère l'ID du client identifié"""
        return self.collected_data.get('client_id')
    
    def is_client_identified(self) -> bool:
        """Vérifie si le client est identifié"""
        return self.client_info is not None
    
    def set_active_form(self, form_name: str):
        """Active un formulaire"""
        self.active_form = form_name
        self.state = "waiting_input"
    
    def clear_active_form(self):
        """Désactive le formulaire actif"""
        self.active_form = None
        if self.state == "waiting_input":
            self.state = "active"
    
    def has_active_form(self) -> bool:
        """Vérifie s'il y a un formulaire actif"""
        return self.active_form is not None
    
    def add_collected_data(self, key: str, value: Any):
        """Ajoute une donnée collectée"""
        self.collected_data[key] = value
    
    def get_collected_data(self, key: str, default: Any = None) -> Any:
        """Récupère une donnée collectée"""
        return self.collected_data.get(key, default)
    
    def set_current_agent(self, agent_name: str):
        """Définit l'agent actuel"""
        self.current_agent = agent_name
        self.agent_history.append({
            'agent': agent_name,
            'timestamp': datetime.now().isoformat()
        })
    
    def set_current_intent(self, intent: str):
        """Définit l'intention actuelle"""
        self.current_intent = intent
        self.intent_history.append({
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_last_intent(self) -> Optional[str]:
        """Récupère la dernière intention"""
        return self.current_intent
    
    def cache_query_result(self, query_name: str, params: Dict, result: Any):
        """
        Met en cache le résultat d'une requête
        
        Args:
            query_name: Nom de la requête
            params: Paramètres de la requête
            result: Résultat à cacher
        """
        cache_key = self._make_cache_key(query_name, params)
        self.query_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now(),
            'query_name': query_name
        }
    
    def get_cached_query(self, query_name: str, params: Dict) -> Optional[Any]:
        """
        Récupère un résultat de requête du cache
        
        Args:
            query_name: Nom de la requête
            params: Paramètres de la requête
            
        Returns:
            Résultat caché ou None si expiré/absent
        """
        cache_key = self._make_cache_key(query_name, params)
        cached = self.query_cache.get(cache_key)
        
        if not cached:
            return None
        
        # Vérifier expiration
        if datetime.now() - cached['timestamp'] > self.cache_ttl:
            del self.query_cache[cache_key]
            return None
        
        return cached['result']
    
    def clear_cache(self):
        """Vide le cache des requêtes"""
        self.query_cache = {}
    
    def _make_cache_key(self, query_name: str, params: Dict) -> str:
        """Crée une clé de cache unique"""
        params_str = json.dumps(params, sort_keys=True)
        return f"{query_name}:{params_str}"
    
    def get_session_duration(self) -> timedelta:
        """Récupère la durée de la session"""
        return datetime.now() - self.created_at
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """
        Vérifie si la session est expirée
        
        Args:
            timeout_minutes: Timeout en minutes
            
        Returns:
            bool: True si expiré
        """
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)
    
    def to_dict(self) -> Dict:
        """Exporte le contexte en dictionnaire"""
        return {
            'conversation_id': self.conversation_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'history': list(self.history),
            'collected_data': self.collected_data,
            'client_info': self.client_info,
            'active_form': self.active_form,
            'current_agent': self.current_agent,
            'current_intent': self.current_intent,
            'state': self.state,
            'metadata': self.metadata
        }


class ContextManager:
    """Gestionnaire global de tous les contextes de conversation"""
    
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}
        self.cleanup_interval = timedelta(hours=1)
        self.last_cleanup = datetime.now()
    
    def get_or_create_context(self, conversation_id: str) -> ConversationContext:
        """
        Récupère ou crée un contexte de conversation
        
        Args:
            conversation_id: ID de la conversation
            
        Returns:
            ConversationContext: Contexte de la conversation
        """
        if conversation_id not in self.contexts:
            self.contexts[conversation_id] = ConversationContext(conversation_id)
        else:
            # Mettre à jour l'activité
            self.contexts[conversation_id].last_activity = datetime.now()
        
        # Nettoyage périodique
        self._maybe_cleanup()
        
        return self.contexts[conversation_id]
    
    def get_context(self, conversation_id: str) -> Optional[ConversationContext]:
        """Récupère un contexte existant"""
        return self.contexts.get(conversation_id)
    
    def delete_context(self, conversation_id: str):
        """Supprime un contexte"""
        if conversation_id in self.contexts:
            del self.contexts[conversation_id]
    
    def list_active_contexts(self) -> List[str]:
        """Liste les IDs des contextes actifs"""
        return list(self.contexts.keys())
    
    def get_active_count(self) -> int:
        """Retourne le nombre de contextes actifs"""
        return len(self.contexts)
    
    def _maybe_cleanup(self):
        """Nettoie périodiquement les contextes expirés"""
        if datetime.now() - self.last_cleanup < self.cleanup_interval:
            return
        
        expired_contexts = []
        for conv_id, context in self.contexts.items():
            if context.is_expired():
                expired_contexts.append(conv_id)
        
        for conv_id in expired_contexts:
            del self.contexts[conv_id]
        
        self.last_cleanup = datetime.now()
        
        if expired_contexts:
            print(f"[ContextManager] Nettoyé {len(expired_contexts)} contextes expirés")
    
    def cleanup_all(self):
        """Force le nettoyage de tous les contextes expirés"""
        expired = [conv_id for conv_id, ctx in self.contexts.items() if ctx.is_expired()]
        for conv_id in expired:
            del self.contexts[conv_id]
        return len(expired)


# ============================================================================
# INSTANCE GLOBALE
# ============================================================================

# Instance partagée du gestionnaire de contexte
_context_manager = None


def get_context_manager() -> ContextManager:
    """Récupère l'instance globale du gestionnaire de contexte"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def summarize_conversation(context: ConversationContext, max_messages: int = 10) -> str:
    """
    Résume une conversation pour fournir du contexte aux agents
    
    Args:
        context: Contexte de la conversation
        max_messages: Nombre maximum de messages à inclure
        
    Returns:
        str: Résumé formaté
    """
    history = context.get_history(max_messages)
    
    summary_lines = [
        f"=== Contexte de conversation ===",
        f"Durée: {context.get_session_duration()}",
        f"Client identifié: {'Oui' if context.is_client_identified() else 'Non'}",
    ]
    
    if context.client_info:
        summary_lines.append(f"Client: {context.client_info.get('username')} (Ref: {context.client_info.get('client_reference')})")
    
    if context.current_intent:
        summary_lines.append(f"Intention actuelle: {context.current_intent}")
    
    if context.active_form:
        summary_lines.append(f"Formulaire actif: {context.active_form}")
    
    summary_lines.append("\n=== Historique récent ===")
    
    for msg in history[-5:]:  # 5 derniers messages
        role_label = "Utilisateur" if msg['role'] == 'user' else "Assistant"
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        summary_lines.append(f"{role_label}: {content}")
    
    return "\n".join(summary_lines)


def extract_context_for_agent(context: ConversationContext) -> Dict:
    """
    Extrait les informations pertinentes pour un agent
    
    Args:
        context: Contexte de la conversation
        
    Returns:
        dict: Données contextuelles pour l'agent
    """
    return {
        'client_id': context.get_client_id(),
        'client_reference': context.collected_data.get('client_reference'),
        'collected_data': context.collected_data,
        'last_intent': context.get_last_intent(),
        'conversation_history': context.get_history(5),  # 5 derniers messages
        'is_client_identified': context.is_client_identified(),
        'session_duration': str(context.get_session_duration()),
    }
