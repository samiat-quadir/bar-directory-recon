# Utility to check the health of various modules
import logging


def check_module_health(module_name):
    try:
        # Simulate health check logic
        logging.info(f"Checking health for module: {module_name}")
        return {"module": module_name, "status": "healthy"}
    except Exception as e:
        logging.error(f"Health check failed for {module_name}: {str(e)}")
        return {"module": module_name, "status": "unhealthy", "error": str(e)}
