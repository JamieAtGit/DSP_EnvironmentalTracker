"""
Enhanced File Validation for Security
====================================

Comprehensive file validation to prevent malicious uploads.
"""

import os
import mimetypes
import magic
from werkzeug.utils import secure_filename
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SecureFileValidator:
    """Secure file validation with multiple checks"""
    
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    ALLOWED_MIMETYPES = {
        'csv': ['text/csv', 'application/csv'],
        'json': ['application/json', 'text/json'],
        'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        'txt': ['text/plain']
    }
    
    @classmethod
    def validate_file(cls, file) -> tuple[bool, str]:
        """Comprehensive file validation"""
        try:
            # Check if file exists
            if not file or not file.filename:
                return False, "No file provided"
            
            # Secure filename
            filename = secure_filename(file.filename)
            if not filename:
                return False, "Invalid filename"
            
            # Check file extension
            file_ext = cls._get_file_extension(filename)
            if file_ext not in cls.ALLOWED_EXTENSIONS:
                return False, f"File type '{file_ext}' not allowed"
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset position
            
            if file_size > cls.MAX_FILE_SIZE:
                return False, f"File too large (max {cls.MAX_FILE_SIZE // 1024 // 1024}MB)"
            
            if file_size == 0:
                return False, "Empty file not allowed"
            
            # Check MIME type
            if not cls._validate_mimetype(file, file_ext):
                return False, "File content doesn't match extension"
            
            # Check for malicious content
            if not cls._scan_content(file):
                return False, "Potentially malicious content detected"
            
            return True, "File validation passed"
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False, "File validation failed"
    
    @classmethod
    def _get_file_extension(cls, filename: str) -> str:
        """Get file extension safely"""
        return Path(filename).suffix.lower().lstrip('.')
    
    @classmethod
    def _validate_mimetype(cls, file, expected_ext: str) -> bool:
        """Validate file MIME type matches extension"""
        try:
            # Read first chunk to determine MIME type
            chunk = file.read(1024)
            file.seek(0)  # Reset position
            
            # Use python-magic for MIME type detection
            mime_type = magic.from_buffer(chunk, mime=True)
            
            allowed_mimes = cls.ALLOWED_MIMETYPES.get(expected_ext, [])
            return mime_type in allowed_mimes
            
        except Exception:
            # If MIME detection fails, rely on extension validation
            return True
    
    @classmethod
    def _scan_content(cls, file) -> bool:
        """Basic content scanning for malicious patterns"""
        try:
            # Read file content for scanning
            content = file.read()
            file.seek(0)  # Reset position
            
            # Convert to string for text files
            try:
                text_content = content.decode('utf-8', errors='ignore').lower()
            except:
                # Binary file, skip text-based checks
                return True
            
            # Check for suspicious patterns
            suspicious_patterns = [
                '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
                'eval(', 'exec(', '__import__', 'subprocess', 'os.system'
            ]
            
            for pattern in suspicious_patterns:
                if pattern in text_content:
                    logger.warning(f"Suspicious pattern detected: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Content scanning error: {e}")
            return False

def validate_upload(file):
    """Convenience function for file validation"""
    return SecureFileValidator.validate_file(file)

# Example usage:
# valid, message = validate_upload(uploaded_file)
# if not valid:
#     return {"error": message}, 400
