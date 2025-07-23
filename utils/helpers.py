def map_area(area):
    """Map responsibility areas to standardized categories."""
    area = str(area).upper()
    if any(k in area for k in ["CCR", "NCU"]):
        return "NCU"
    if "NCAU" in area:
        return "NCAU"
    if "IOP ECR" in area:
        return "IOP ECR"
    if "IOP NCR" in area:
        return "IOP NCR"
    if "IOP SCR" in area:
        return "IOP SCR"
    if any(k in area for k in ["CPP", "POWER PLANT"]):
        return "CPP"
    if "HDPE" in area:
        return "HDPE"
    if "LLDPE" in area:
        return "LLDPE"
    if "BAGGING" in area:
        return "IOP BAGGING"
    if any(k in area for k in ["ADMINISTRATION", "HPL", "LOGISTICS", "OSBL"]):
        return "OTHERS"
    if any(k in area for k in ["HSEF", "FIRE", "SAFETY"]):
        return "HSEF"
    return "OTHERS"