import os
import sys
import logging
from pathlib import Path
from src.utils.installation_manager import InstallationManager

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('installation.log')
        ]
    )

def main():
    setup_logging()
    logging.info("Starting AI OS installation process...")
    
    # Initialize installation manager
    manager = InstallationManager()
    
    try:
        # Add installations
        g_drive_success = manager.add_installation(
            drive="G",
            name="AI_OS_Primary",
            is_primary=True
        )
        
        f_drive_success = manager.add_installation(
            drive="F",
            name="AI_OS_Secondary",
            is_primary=False
        )
        
        if g_drive_success and f_drive_success:
            logging.info("Successfully created both installations")
            
            # Validate installations
            g_validation = manager.validate_installation("G")
            f_validation = manager.validate_installation("F")
            
            logging.info("\nG: Drive Installation Status:")
            logging.info(f"Exists: {g_validation['exists']}")
            logging.info(f"Space Available: {g_validation['space_available'] // (1024*1024*1024)}GB")
            logging.info("Directory Status:", g_validation['directories'])
            
            logging.info("\nF: Drive Installation Status:")
            logging.info(f"Exists: {f_validation['exists']}")
            logging.info(f"Space Available: {f_validation['space_available'] // (1024*1024*1024)}GB")
            logging.info("Directory Status:", f_validation['directories'])
            
            # Initial sync from G to F
            sync_success = manager.sync_installations(
                source_drive="G",
                target_drive="F",
                sync_data=True,
                sync_models=True,
                sync_config=True
            )
            
            if sync_success:
                logging.info("Initial synchronization completed successfully")
            else:
                logging.warning("Initial synchronization failed")
            
        else:
            if not g_drive_success:
                logging.error("Failed to create G: drive installation")
            if not f_drive_success:
                logging.error("Failed to create F: drive installation")
            
    except Exception as e:
        logging.error(f"Installation failed: {str(e)}")
        return 1
    
    logging.info("Installation process completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
