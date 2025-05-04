from argostranslate import package, translate

def setup_translation_models(target_langs=["en", "fr", "es", "de", "hi"]):
    package.update_package_index()
    available = package.get_available_packages()
    
    def has_model(frm, to):
        return any(p.from_code == frm and p.to_code == to for p in available)

    def install_model(frm, to):
        for inst in package.get_installed_packages():
            if inst.from_code == frm and inst.to_code == to:
                return
        
        pkg = next((p for p in available if p.from_code == frm and p.to_code == to), None)
        if not pkg:
            raise RuntimeError(f"Модель {frm}→{to} не найдена")
        
        path = pkg.download()
        package.install_from_path(path)

    install_model("ru", "en")
    for lang in target_langs:
        if lang != "en":
            if has_model("ru", lang):
                install_model("ru", lang)
            else:
                install_model("en", lang)

def smart_translate(text, frm, to):
    if has_model(frm, to):
        return translate.translate(text, frm, to)
    
    mid = "en"
    return translate.translate(
        translate.translate(text, frm, mid),
        mid, to
    )

def has_model(frm, to):
    available = package.get_available_packages()
    return any(p.from_code == frm and p.to_code == to for p in available)