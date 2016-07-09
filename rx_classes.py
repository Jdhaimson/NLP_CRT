from umls.rxnorm import RxNormLookup

def get_rx_classes(drug_str, include_name=False):
    rxclasses = []
    lookup = RxNormLookup()
    try:
        rxcui = lookup.rxcui_for_name_approx(drug_str)
        if rxcui:
            rxclasses = lookup.rxclass_for_rxcui(rxcui)
            if include_name:
                name = lookup.lookup_rxcui_name(rxcui)
        else:
            rxclasses = []
            name = None
    except Exception:
        rxclasses = []
        name = None

    if include_name:
        return (name, rxclasses)
    else:
        return rxclasses
