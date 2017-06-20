"""
Lists of constants that can be used in the video xblock.
"""

DEFAULT_LANG = 'en'


class PlayerName(object):
    """
    Contains Player names for each backends.
    """

    BRIGHTCOVE = 'brightcove-player'
    DUMMY = 'dummy-player'
    HTML5 = 'html5-player'
    VIMEO = 'vimeo-player'
    WISTIA = 'wistia-player'
    YOUTUBE = 'youtube-player'


class TPMApiTranscriptFormatID(object):
    """
    3PlayMedia service's transcripts API format_name - format_ID mapping.

    Full list can be got by GET to "http://static.3playmedia.com/output_formats?apikey=foo".
    """

    SRT = 7
    JSON = 29
    PDF = 46
    WEBVTT = 51


class TPMApiLanguage(object):
    """
    3PlayMedia service's transcripts API language_ID - language info (e.g.: code, name...) mapping.

    Full list can be got by GET to "http://api.3playmedia.com/caption_imports/available_languages?apikey=:api_key"
    """

    TPM_LANGUAGES = {
        1: {
            "ietf_code": "en",
            "iso_639_1_code": "en",
            "name": "English",
            "full_name": "English",
            "description": "All English variants"
        },
        3: {
            "ietf_code": "en",
            "iso_639_1_code": "en",
            "name": "English",
            "full_name": "English (GB)",
            "description": "English as spoken/written in Great Britain"
        },
        5: {
            "ietf_code": "fr",
            "iso_639_1_code": "fr",
            "name": "French",
            "full_name": "French (France)",
            "description": "French as spoken/written in France"
        },
        6: {
            "ietf_code": "fr",
            "iso_639_1_code": "fr",
            "name": "French",
            "full_name": "French (Canada)",
            "description": "French as spoken/written in Canada"
        },
        7: {
            "ietf_code": "de",
            "iso_639_1_code": "de",
            "name": "German",
            "full_name": "German",
            "description": "German as spoken/written in Germany"
        },
        8: {
            "ietf_code": "it",
            "iso_639_1_code": "it",
            "name": "Italian",
            "full_name": "Italian",
            "description": "Italian as spoken/written in Italy"
        },
        9: {
            "ietf_code": "nl",
            "iso_639_1_code": "nl",
            "name": "Dutch",
            "full_name": "Dutch",
            "description": "Dutch as spoken/written in The Netherlands"
        },
        10: {
            "ietf_code": "el",
            "iso_639_1_code": "el",
            "name": "Greek",
            "full_name": "Greek",
            "description": "Greek as spoken/written in Greece"
        },
        12: {
            "ietf_code": "es",
            "iso_639_1_code": "es",
            "name": "Spanish",
            "full_name": "Spanish (Spain)",
            "description": "Castilian Spanish as spoken/written in Spain"
        },
        13: {
            "ietf_code": "es-419",
            "iso_639_1_code": "es",
            "name": "Spanish",
            "full_name": "Spanish (Latin America)",
            "description": "Spanish as spoken/written in Latin America"
        },
        15: {
            "ietf_code": "pt",
            "iso_639_1_code": "pt",
            "name": "Portuguese",
            "full_name": "Portuguese (Portugal)",
            "description": "Portuguese as spoken/written in Portugal"
        },
        16: {
            "ietf_code": "pt",
            "iso_639_1_code": "pt",
            "name": "Portuguese",
            "full_name": "Portuguese (Brazil)",
            "description": "Portuguese as spoken/written in Brazil"
        },
        18: {
            "ietf_code": "zh-hans",
            "iso_639_1_code": "zh",
            "name": "Chinese",
            "full_name": "Chinese (Simplified)",
            "description": "Simplified Chinese"
        },
        19: {
            "ietf_code": "zh-cmn-Hant",
            "iso_639_1_code": "zh",
            "name": "Chinese",
            "full_name": "Chinese (Traditional)",
            "description": "Mandarin Chinese (Traditional)"
        },
        20: {
            "ietf_code": "ar",
            "iso_639_1_code": "ar",
            "name": "Arabic",
            "full_name": "Arabic",
            "description": "All Arabic Variants"
        },
        21: {
            "ietf_code": "he",
            "iso_639_1_code": "he",
            "name": "Hebrew",
            "full_name": "Hebrew",
            "description": "All Hebrew Variants"
        },
        22: {
            "ietf_code": "ru",
            "iso_639_1_code": "ru",
            "name": "Russian",
            "full_name": "Russian",
            "description": "All Russian Variants"
        },
        23: {
            "ietf_code": "ja",
            "iso_639_1_code": "ja",
            "name": "Japanese",
            "full_name": "Japanese",
            "description": "All Japanese Variants"
        },
        26: {
            "ietf_code": "",
            "iso_639_1_code": "sv",
            "name": "Swedish",
            "full_name": "Swedish",
            "description": ""
        },
        27: {
            "ietf_code": "",
            "iso_639_1_code": "cs",
            "name": "Czech",
            "full_name": "Czech",
            "description": ""
        },
        28: {
            "ietf_code": "",
            "iso_639_1_code": "da",
            "name": "Danish",
            "full_name": "Danish",
            "description": ""
        },
        29: {
            "ietf_code": "",
            "iso_639_1_code": "fi",
            "name": "Finnish",
            "full_name": "Finnish",
            "description": ""
        },
        30: {
            "ietf_code": "",
            "iso_639_1_code": "id",
            "name": "Indonesian",
            "full_name": "Indonesian",
            "description": ""
        },
        31: {
            "ietf_code": "",
            "iso_639_1_code": "ko",
            "name": "Korean",
            "full_name": "Korean",
            "description": ""
        },
        32: {
            "ietf_code": "",
            "iso_639_1_code": "no",
            "name": "Norwegian",
            "full_name": "Norwegian",
            "description": ""
        },
        33: {
            "ietf_code": "",
            "iso_639_1_code": "pl",
            "name": "Polish",
            "full_name": "Polish",
            "description": ""
        },
        34: {
            "ietf_code": "",
            "iso_639_1_code": "th",
            "name": "Thai",
            "full_name": "Thai",
            "description": ""
        },
        35: {
            "ietf_code": "",
            "iso_639_1_code": "tr",
            "name": "Turkish",
            "full_name": "Turkish",
            "description": ""
        },
        36: {
            "ietf_code": "",
            "iso_639_1_code": "vi",
            "name": "Vietnamese",
            "full_name": "Vietnamese",
            "description": ""
        },
        37: {
            "ietf_code": "",
            "iso_639_1_code": "ro",
            "name": "Romanian",
            "full_name": "Romanian",
            "description": ""
        },
        38: {
            "ietf_code": "",
            "iso_639_1_code": "hu",
            "name": "Hungarian",
            "full_name": "Hungarian",
            "description": ""
        },
        39: {
            "ietf_code": "",
            "iso_639_1_code": "ms",
            "name": "Malay",
            "full_name": "Malay",
            "description": ""
        },
        40: {
            "ietf_code": "",
            "iso_639_1_code": "bg",
            "name": "Bulgarian",
            "full_name": "Bulgarian",
            "description": ""
        },
        41: {
            "ietf_code": "",
            "iso_639_1_code": "tl",
            "name": "Tagalog",
            "full_name": "Tagalog",
            "description": ""
        },
        46: {
            "ietf_code": "",
            "iso_639_1_code": "sr",
            "name": "Serbian",
            "full_name": "Serbian",
            "description": ""
        },
        47: {
            "ietf_code": "",
            "iso_639_1_code": "sk",
            "name": "Slovak",
            "full_name": "Slovak",
            "description": ""
        },
        48: {
            "ietf_code": "",
            "iso_639_1_code": "uk",
            "name": "Ukrainian",
            "full_name": "Ukrainian",
            "description": ""
        }
    }

    def __init__(self, language_id):
        """
        Initiate 3PlayMedia language information based on given language ID.

        :param language_id : int (from API response list of available transcript translations).
        """
        if language_id not in self.TPM_LANGUAGES.keys():
            raise ValueError("Language ID: {} does not exist!".format(language_id))
        language_info = self.TPM_LANGUAGES[language_id]
        self.language_id = language_id
        self.ietf_code = language_info.get("ietf_code")
        self.iso_639_1_code = language_info.get("iso_639_1_code")
        self.name = language_info.get("name")
        self.full_name = language_info.get("full_name")
        self.description = language_info.get("description")
