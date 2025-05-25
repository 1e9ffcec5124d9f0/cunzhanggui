

from datetime import datetime, timezone
from typing import Optional,List,Dict
from sqlalchemy import JSON
from sqlmodel import SQLModel,Field, Session, select
from core.configs import DEBUG_MODE, application_sqlmodel_engine
from core.crypto.sm2_crypto import SM2Crypto
from flask import Blueprint, request, jsonify

crypto_blueprint = Blueprint('crypto', __name__, url_prefix='/api/crypto')



@crypto_blueprint.route('/get_public_key', methods=['GET'])
def get_public_key():
    """获取公钥"""
    public_key = SM2Crypto.get_public_key()
    return jsonify({"code": 200, "message": "获取公钥成功", "public_key": public_key}), 200


