# coding: utf-8
#
# Copyright © Lyra Network.
# This file is part of OSB plugin for Odoo. See COPYING.md for license details.
#
# Author:    Lyra Network (https://www.lyra.com)
# Copyright: Copyright © Lyra Network
# License:   http://www.gnu.org/licenses/agpl.html GNU Affero General Public License (AGPL v3)

from odoo import _

# WARN: Do not modify code format here. This is managed by build files.
OSB_PLUGIN_FEATURES = {
    'multi': True,
    'restrictmulti': False,
    'qualif': False,
    'shatwo': True,
}

OSB_PARAMS = {
    'GATEWAY_CODE': 'OSB',
    'GATEWAY_NAME': 'OSB',
    'BACKOFFICE_NAME': 'OSB',
    'SUPPORT_EMAIL': 'support@osb.pf',
    'GATEWAY_URL': 'https://secure.osb.pf/vads-payment/',
    'SITE_ID': '12345678',
    'KEY_TEST': '1111111111111111',
    'KEY_PROD': '2222222222222222',
    'CTX_MODE': 'TEST',
    'SIGN_ALGO': 'SHA-256',
    'LANGUAGE': 'fr',

    'GATEWAY_VERSION': 'V2',
    'PLUGIN_VERSION': '2.0.1',
    'CMS_IDENTIFIER': 'Odoo_15',
}

OSB_LANGUAGES = {
    'cn': 'Chinese',
    'de': 'German',
    'es': 'Spanish',
    'en': 'English',
    'fr': 'French',
    'it': 'Italian',
    'jp': 'Japanese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'sv': 'Swedish',
    'tr': 'Turkish',
}

OSB_CARDS = {
    'CB': u'CB',
    'E-CARTEBLEUE': u'e-Carte Bleue',
    'MAESTRO': u'Maestro',
    'MASTERCARD': u'Mastercard',
    'VISA': u'Visa',
    'VISA_ELECTRON': u'Visa Electron',
    'VPAY': u'V PAY',
    'AMEX': u'American Express',
    'DINERS': u'Diners',
    'DISCOVER': u'Discover',
    'GOOGLEPAY': u'Google Pay',
    'JCB': u'JCB',
    'PAYPAL': u'PayPal',
    'PAYPAL_SB': u'PayPal Sandbox',
    'PRV_BDP': u'Banque de Polynésie',
    'PRV_BDT': u'Banque de Tahiti',
    'PRV_OPT': u'OPT',
    'PRV_SOC': u'Banque Socredo',
    'PRV_SOC_GOLD': u'Banque Socredo Gold',
    'PRV_SOC_VERTE': u'Banque Socredo Verte',
}

OSB_CURRENCIES = [
    ['XPF', '953', 0],
]
