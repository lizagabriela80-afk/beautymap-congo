"""
Service OTP BeautyMap Congo
DEBUG=True  → affiche le code dans la console et la page (pas de SMS)
DEBUG=False → envoie un vrai SMS via Africa's Talking
"""
import random
import string
from django.conf import settings


def generate_code(length=6):
    """Génère un code numérique à 6 chiffres."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp(phone: str, code: str) -> dict:
    """
    Envoie le code OTP.
    En mode DEBUG : affiche dans la console, retourne le code.
    En production : envoie un SMS via Africa's Talking.
    """
    if settings.DEBUG:
        print("\n" + "=" * 50)
        print("  📲  BeautyMap Congo — OTP DEBUG")
        print(f"  Numéro : {phone}")
        print(f"  Code   : {code}")
        print("  ⚠️  Aucun SMS envoyé (DEBUG=True)")
        print("=" * 50 + "\n")
        return {
            'success': True,
            'channel': 'console',
            'code': code,
        }

    # Production : Africa's Talking
    return _send_sms_africastalking(phone, code)


def _send_sms_africastalking(phone: str, code: str) -> dict:
    """Envoie le SMS via Africa's Talking. Fonctionne avec +242 (Congo)."""
    try:
        import africastalking

        africastalking.initialize(
            username=getattr(settings, 'AT_USERNAME', 'sandbox'),
            api_key=getattr(settings, 'AT_API_KEY', ''),
        )

        sms = africastalking.SMS

        if not phone.startswith('+'):
            phone = '+' + phone

        message = (
            f"BeautyMap Congo\n"
            f"Votre code : {code}\n"
            f"Valable 5 minutes.\n"
            f"Ne le partagez pas."
        )

        sender   = getattr(settings, 'AT_SENDER', None)
        response = sms.send(message, [phone], sender_id=sender)
        recipients = response.get('SMSMessageData', {}).get('Recipients', [])

        if recipients and recipients[0].get('status') == 'Success':
            print(f"✅ SMS envoyé à {phone}")
            return {'success': True, 'channel': 'sms_at'}
        else:
            err = recipients[0].get('status', 'Erreur') if recipients else 'Pas de réponse'
            print(f"❌ Échec SMS : {err}")
            return {'success': False, 'error': err}

    except ImportError:
        print("❌ Installez africastalking : pip install africastalking")
        return {'success': False, 'error': "Package africastalking manquant"}
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return {'success': False, 'error': str(e)}