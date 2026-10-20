# Where I am unsure of a translation, and why. Everything not listed here is still only
# DRAFT: written by Claude, checked for form, not read by a native speaker.

DRAVIDIAN = {'tamil', 'telugu', 'kannada', 'malayalam'}

# applies to every pack
COMMON = {
 'r7_msg_arity3': "The count is printed before this text and is often 1 ('f' … 1 …): the noun is in the plural form, so '1 <plural>' may read wrong. A fragment cannot change with the number.",
 'r7_msg_arity2': "Word order is fixed by the code: 'NAME' <this> N <arity3> M. Check that the sentence reads naturally around the name and the two numbers.",
 'msg_lang_ok': "'pack' (the language-pack file) has no settled native word; check the term.",
 'msg_lang_fail': "The same term for 'pack' as msg_lang_ok.",
 'msg_ast_overflow': "'syntax tree' is a coined technical term here; check it.",
 'r48_msg_near': "'word' stands for a token; check that it reads naturally before the quoted token.",
 'mg_e_noexp2': "Order fixed by the code: 'SYM' <this> 'MOD' <noexp3>. Check that 'SYM … MOD … not exported' reads as one sentence.",
 'r55_msg_proto_signature': "'forward declaration' (a prototype) is a coined term; check it.",
 'msg_shell_banner': "'Enter' is kept as the key's label; the verb for pressing a key should be checked.",
}

PACK = {
'sanskrit': {
 'r52_msg_charcode_arity': "'1 वा 2 तर्कौ' uses the dual, which agrees with 2 but not with 1. I could not find a form that fits both; please choose.",
 'r52_msg_dvaram_arity': "'2 वा 3 तर्काः': plural for both; check.",
 'r7_msg_arity2': "'इत्यस्मै' (the dative of the name, marked with इति) is my construction; a speaker may prefer another way to mark a name as the recipient.",
 'r4_msg_hint_old2': "'कुञ्जीशब्दः' for keyword follows the project's romanised 'kunjishabd'; and 'v157 तः' attaches the ablative to a Latin token. Both should be checked.",
 'msg_array_oob': "'अङ्कः' for an index can also mean 'number'; and the pack's word for mala is 'पङ्क्ति' (a row), so this reads 'row-number beyond the limit'. Check that it is understood as an array index.",
 'msg_kosh_required': "'वित्ति' is the project's coined keyword; I treated it as feminine (आवश्यकी). Check the gender.",
 'msg_namespace_error': "LIKELY WRONG: 'अशुद्धः' is masculine, but the pack's word for yoj, 'आयोजन', is neuter (आयोजनम्). The keyword is inserted in its stem form, so the adjective should probably be 'अशुद्धम्' or the phrase recast.",
 'msg_bytes': "'बाइट्' is the Sanskrit book's loanword; I made the participle masculine plural (सङ्कलिताः). Check the agreement.",
 'msg_lang_ok': "'भाषा-पुटः' is my coinage for 'language pack' (alternatives: भाषा-सम्पुटः, भाषा-सङ्ग्रहः).",
 'msg_shell_banner': "'नुदतु' (push) for pressing a key is my choice; check it.",
 'mg_e_noexp2': "'SYM' घटकात् 'MOD' अनिर्यातम्: the ablative 'from the module' comes before the module's name; check the order.",
 'ide.st_sanchit_w': "'सञ्चितम्' for a saved file; check the term.",
 'ide.st_asanchit_w': "As st_sanchit_w.",
 'ide.lang_swayam_w': "'स्वयम्' for the Auto (detect) setting; 'स्वचालितम्' may be clearer.",
 'ide.msg_timeout': "'क्षणः' for a second follows modern spoken Sanskrit as I understand it; check.",
 'ide.msg_pipe_fail': "'नालिका' for a pipe (an operating-system channel) is a literal coinage.",
 'r65_msg_add': "'अतिप्रवाहः' for an integer overflow is a calque; it is used in all seven trap messages.",
 'r4_msg_hint_decl': "'सूचना' is used for every hint (the default says 'Sanket'); I avoided 'सङ्केतः:' because the visarga followed by a colon looked like '::'.",
},
'hindi': {
 'r7_msg_arity3': "'हस्ताक्षर' for a function signature is a literal calque; check whether a Hindi programmer would say this.",
 'r4_msg_hint_old2': "'कुंजीशब्द' for keyword; 'मुख्य शब्द' or the loan 'कीवर्ड' may be more usual.",
 'msg_array_oob': "The pack's word for mala is 'पंक्ति' (a row/line), so this reads 'row index out of bounds'.",
 'ide.msg_pipe_fail': "'नलिका' for a pipe is a literal coinage.",
 'r65_msg_add': "'अतिप्रवाह' for overflow (all seven trap messages): check the term.",
 'msg_namespace_module_missing': "'मॉड्यूल' is a loanword, as in the project's Hindi book; a native term ('घटक') is possible if loans are unwanted.",
},
'marathi': {
 'r7_msg_arity3': "'युक्तिवाद' for an argument is the debating/legal sense; a Marathi programmer may say 'मापदंड' or 'आर्ग्युमेंट'. Also 'स्वाक्षरी' for a signature is a calque.",
 'r4_msg_hint_old2': "'कळशब्द' for keyword is my coinage; check.",
 'msg_array_oob': "The pack's word for mala is 'रांग' (a queue/row); check that 'रांग निर्देशांक' is understood as an array index.",
 'r48_msg_errors': "Uses 'दोष' for errors; check against the usual 'त्रुटी'.",
},
'gujarati': {
 'r7_msg_arity3': "'દલીલ' for an argument is the debating sense; check whether a programmer would use it. 'હસ્તાક્ષર' for a signature is a calque.",
 'r4_msg_hint_old2': "'મુખ્યશબ્દ' for keyword; check.",
 'msg_array_oob': "'અનુક્રમાંક' for an index; check.",
},
'bengali': {
 'r7_msg_arity3': "'যুক্তি' for an argument is the reasoning sense; check. 'স্বাক্ষর' for a signature is a calque.",
 'r4_msg_hint_old2': "'মূলশব্দ' for keyword; check.",
 'r65_msg_add': "'উপচে পড়া' (spilling over) for an integer overflow is colloquial; check (all seven trap messages).",
 'mg_e_noexp3': "'রপ্তানি' (export) is the trade sense; check whether it reads as a module export.",
 'msg_namespace_module_missing': "'মডিউল' is a loanword.",
 'msg_shell_bye': "'অধিবেশন' for a session; check.",
},
'punjabi': {
 'msg_shell_bye': "LIKELY TO CHANGE: 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ' is a Sikh greeting; a neutral 'ਨਮਸਤੇ' may be preferred for every user. Please decide.",
 'r7_msg_arity3': "'ਤਰਕ' for an argument and 'ਦਸਤਖ਼ਤ' for a signature are calques; check.",
 'r4_msg_hint_old2': "'ਮੁੱਖ-ਸ਼ਬਦ' for keyword; check.",
 'msg_kosh_required': "The pack's own word for vitti is 'ਵੇਰੀਏਬਲ', an English loan in Gurmukhi; it appears in every message that shows the keyword. That is the pack's choice, not this file's.",
 'r65_msg_add': "'ਅਤਿ-ਪ੍ਰਵਾਹ' for overflow is a calque (all seven trap messages).",
 'msg_namespace_module_missing': "'ਮੌਡਿਊਲ' is a loanword.",
},
'odia': {
 'r7_msg_arity3': "'ଯୁକ୍ତି' for an argument and 'ସ୍ୱାକ୍ଷର' for a signature: check.",
 'r4_msg_hint_old2': "'ମୂଳଶବ୍ଦ' for keyword; check.",
 'mg_e_noexp3': "'ରପ୍ତାନି' (export, trade sense); check.",
 'msg_namespace_module_missing': "'ମଡ୍ୟୁଲ୍' is a loanword.",
 'ide.lang_swayam_w': "'ସ୍ୱୟଂଚାଳିତ' for Auto; check.",
},
'tamil': {
 'msg_array_oob': "The pack's word for mala is 'வரிசைப்பட', which looks like a truncated verb form; it appears wherever the keyword is shown. That is lang/tamil.lang's choice and should be checked there.",
 'r7_msg_arity3': "'அளவுரு' (parameter) is used for an argument; 'கையொப்பம்' for a signature is a calque.",
 'r4_msg_hint_old2': "'முக்கியச்சொல்' for keyword; and 'v157 க்கு' puts the case suffix after a space.",
 'r65_msg_add': "'வழிதல்' for an integer overflow (all seven trap messages); check.",
 'msg_namespace_module_missing': "'கூறு' (component) for a module; check.",
 'ide.msg_ready': "'தொகுத்து இயக்கும்' (compiles and runs): check the verbs.",
},
'telugu': {
 'r7_msg_arity3': "'ప్రమాణాలు' for arguments is my choice and may not be what a Telugu programmer says; 'సంతకం' for a signature is a calque.",
 'r7_msg_mod_missing2': "'సంచయం' for a folder is a guess; check.",
 'r65_msg_add': "'పొంగిపొర్లడం' (boiling over) for an integer overflow is colloquial; check (all seven trap messages).",
 'msg_namespace_module_missing': "'భాగం' (part) for a module; check.",
},
'kannada': {
 'r7_msg_mod_missing2': "LIKELY WRONG: 'ಕೋಶ' is used here for a folder, but ಕೋಶ is also the pack's keyword for kosh (the data structure). The hint becomes ambiguous; a different word for folder is needed.",
 'r7_msg_arity3': "'ಪ್ರಮಾಣ' for an argument is my choice; 'ಸಹಿ' for a signature is a calque.",
 'r65_msg_add': "'ಉಕ್ಕಿ ಹರಿವು' (boiling over) for an integer overflow is colloquial; check (all seven trap messages).",
 'msg_namespace_module_missing': "'ಘಟಕ' for a module; check.",
},
'malayalam': {
 'r7_msg_arity3': "'പ്രമാണം' for an argument is my choice; 'ഒപ്പ്' for a signature is a calque.",
 'r5_msg_field': "'മണ്ഡലം' for a record field is my choice; check.",
 'r65_msg_add': "'കവിഞ്ഞൊഴുക്ക്' for an integer overflow (all seven trap messages); check.",
 'ide.msg_ready': "'സമ്പാദകം' for the editor is my coinage; check.",
},
}

# Dravidian scripts attach case suffixes to the word. The code prints the name, then the
# fragment, and the default begins with "' " (quote, space), which the checker keeps; so the
# suffix comes out separated: 'f' க்கு, not 'f'க்கு.
SUFFIX_NOTE = ("The case suffix is printed after a space ('f' <suffix>); written {lang} normally attaches it to the word (with a quoted code name, say which you prefer). "
               "The checker keeps the default's leading \"' \", so fixing this needs that rule relaxed for this message.")
SUFFIX_KEYS = ['r7_msg_arity2', 'mg_e_noexp3', 'mg_e_undef2', 'mg_e_valias2']
