"""
Sistema de Logging Estruturado
"""
import sys
from typing import Optional, Any
from datetime import datetime
from loguru import logger
from pathlib import Path

from config.settings import settings


class LogManager:
    """Gerenciador centralizado de logs"""
    
    def __init__(self):
        self.logs_dir = settings.BASE_DIR / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.session_logs = []  # Logs da sessão atual
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura o logger"""
        # Remove handler padrão
        logger.remove()
        
        # Console handler com cores
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True
        )
        
        # File handler com rotação
        logger.add(
            self.logs_dir / "app_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="00:00",  # Nova arquivo à meia-noite
            retention="30 days",  # Mantém 30 dias
            compression="zip"  # Comprime logs antigos
        )
    
    def log_node_start(self, node_name: str, input_data: Any = None):
        """Log de início de execução de um nó"""
        msg = f"🟢 Iniciando nó: {node_name}"
        logger.info(msg)
        
        self.session_logs.append({
            "timestamp": datetime.now(),
            "type": "node_start",
            "node": node_name,
            "level": "INFO",
            "message": msg,
            "data": input_data
        })
    
    def log_node_complete(self, node_name: str, output_data: Any = None):
        """Log de conclusão de um nó"""
        msg = f"✅ Nó concluído: {node_name}"
        logger.success(msg)
        
        self.session_logs.append({
            "timestamp": datetime.now(),
            "type": "node_complete",
            "node": node_name,
            "level": "SUCCESS",
            "message": msg,
            "data": output_data
        })
    
    def log_node_error(self, node_name: str, error: Exception):
        """Log de erro em um nó"""
        msg = f"❌ Erro no nó {node_name}: {str(error)}"
        logger.error(msg)
        
        self.session_logs.append({
            "timestamp": datetime.now(),
            "type": "node_error",
            "node": node_name,
            "level": "ERROR",
            "message": msg,
            "error": str(error)
        })
    
    def log_llm_call(
        self, 
        node_name: str, 
        model: str, 
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        cost: Optional[float] = None
    ):
        """Log de chamada LLM"""
        msg = f"🤖 LLM Call [{node_name}]: {model}"
        if tokens_in and tokens_out:
            msg += f" | In: {tokens_in} | Out: {tokens_out}"
        if cost:
            msg += f" | Cost: ${cost:.4f}"
        
        logger.info(msg)
        
        self.session_logs.append({
            "timestamp": datetime.now(),
            "type": "llm_call",
            "node": node_name,
            "level": "INFO",
            "message": msg,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost
        })
    
    def log_validation(self, node_name: str, is_valid: bool, details: str = ""):
        """Log de validação"""
        if is_valid:
            msg = f"✓ Validação OK [{node_name}]"
            if details:
                msg += f": {details}"
            logger.success(msg)
            level = "SUCCESS"
        else:
            msg = f"✗ Validação FALHOU [{node_name}]"
            if details:
                msg += f": {details}"
            logger.warning(msg)
            level = "WARNING"
        
        self.session_logs.append({
            "timestamp": datetime.now(),
            "type": "validation",
            "node": node_name,
            "level": level,
            "message": msg,
            "is_valid": is_valid,
            "details": details
        })
    
    def log_user_input(self, input_type: str, content: str):
        """Log de input do usuário"""
        msg = f"📝 User Input [{input_type}]: {content[:100]}..."
        logger.info(msg)
        
        self.session_logs.append({
            "timestamp": datetime.now(),
            "type": "user_input",
            "level": "INFO",
            "message": msg,
            "input_type": input_type,
            "content": content
        })
    
    def log_checkpoint(self, checkpoint_name: str, state: Any = None):
        """Log de checkpoint importante"""
        msg = f"🔖 Checkpoint: {checkpoint_name}"
        logger.info(msg)
        
        self.session_logs.append({
            "timestamp": datetime.now(),
            "type": "checkpoint",
            "level": "INFO",
            "message": msg,
            "checkpoint": checkpoint_name,
            "state": state
        })
    
    def get_session_logs(self) -> list[dict]:
        """Retorna logs da sessão atual"""
        return self.session_logs.copy()
    
    def clear_session_logs(self):
        """Limpa logs da sessão"""
        self.session_logs = []
    
    def get_logs_summary(self) -> dict:
        """Retorna resumo dos logs"""
        if not self.session_logs:
            return {
                "total": 0,
                "by_level": {},
                "by_type": {},
                "nodes_executed": []
            }
        
        by_level = {}
        by_type = {}
        nodes = set()
        
        for log in self.session_logs:
            # Count by level
            level = log.get("level", "UNKNOWN")
            by_level[level] = by_level.get(level, 0) + 1
            
            # Count by type
            log_type = log.get("type", "unknown")
            by_type[log_type] = by_type.get(log_type, 0) + 1
            
            # Collect nodes
            if "node" in log:
                nodes.add(log["node"])
        
        return {
            "total": len(self.session_logs),
            "by_level": by_level,
            "by_type": by_type,
            "nodes_executed": sorted(list(nodes))
        }
    
    def export_logs_to_file(self, filename: Optional[str] = None) -> Path:
        """
        Exporta logs da sessão para arquivo
        
        Returns:
            Path do arquivo criado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.log"
        
        filepath = self.logs_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"SESSION LOG EXPORT - {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")
            
            for log in self.session_logs:
                f.write(f"[{log['timestamp']}] [{log['level']}] {log['message']}\n")
                if "data" in log and log["data"]:
                    f.write(f"  Data: {log['data']}\n")
                f.write("\n")
        
        logger.info(f"Logs exportados para: {filepath}")
        return filepath


# Singleton global
_log_manager: Optional[LogManager] = None


def get_logger() -> LogManager:
    """Retorna instância singleton do LogManager"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


# Atalhos para funções comuns
def log_node_start(node_name: str, input_data: Any = None):
    get_logger().log_node_start(node_name, input_data)


def log_node_complete(node_name: str, output_data: Any = None):
    get_logger().log_node_complete(node_name, output_data)


def log_node_error(node_name: str, error: Exception):
    get_logger().log_node_error(node_name, error)


def log_llm_call(node_name: str, model: str, **kwargs):
    get_logger().log_llm_call(node_name, model, **kwargs)


def log_validation(node_name: str, is_valid: bool, details: str = ""):
    get_logger().log_validation(node_name, is_valid, details)