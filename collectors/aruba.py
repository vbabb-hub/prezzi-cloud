from common import vm

URL_ARUBA = "https://www.arubacloud.com/"

def collect():
    records = []

    # 1. Cloud VPS (Serie Smart / Entry Level)
    vps_plans = [
        ("VPS Small (O1I1)", 1, 1, 2.49),
        ("VPS Medium (O1I2)", 1, 2, 4.49),
        ("VPS Large (O2A4)", 2, 4, 6.29),
        ("VPS Extra Large (O4A8)", 4, 8, 11.79),
    ]
    for sku, vcpu, ram, monthly in vps_plans:
        records.append(vm(
            provider="Aruba Cloud",
            region="IT-Arezzo/Bergamo",
            sku=f"Cloud VPS {sku}",
            vcpu=vcpu,
            ram=ram,
            hourly=round(monthly / 730, 4),
            monthly=monthly,
            source=URL_ARUBA,
            note="VPS entry-level con risorse condivise"
        ))

    # 2. OpenStack Pro (General Purpose - Proporzione 1 vCPU : 2GB / 4GB RAM)
    pro_plans = [
        ("PRO O1A2", 1, 2, 0.019),
        ("PRO O2A4", 2, 4, 0.029),
        ("PRO O4A8", 4, 8, 0.045),
        ("PRO O8A16", 8, 16, 0.080),
        ("PRO O12A24", 12, 24, 0.140),
        ("PRO O16A32", 16, 32, 0.220),
        ("PRO O24A48", 24, 48, 0.330),
        ("PRO O32A64", 32, 64, 0.440),
    ]
    for sku, vcpu, ram, h_price in pro_plans:
        records.append(vm(
            provider="Aruba Cloud",
            region="IT-Arezzo/Bergamo",
            sku=f"OpenStack {sku}",
            vcpu=vcpu,
            ram=ram,
            hourly=h_price,
            monthly=round(h_price * 730, 2),
            source=URL_ARUBA
        ))

    # 3. OpenStack High RAM (Memory Optimized)
    ram_plans = [
        ("PRO RAM O2A8", 2, 8, 0.042),
        ("PRO RAM O4A16", 4, 16, 0.075),
        ("PRO RAM O8A32", 8, 32, 0.135),
        ("PRO RAM O16A64", 16, 64, 0.280),
    ]
    for sku, vcpu, ram, h_price in ram_plans:
        records.append(vm(
            provider="Aruba Cloud",
            region="IT-Arezzo/Bergamo",
            sku=f"OpenStack {sku}",
            vcpu=vcpu,
            ram=ram,
            hourly=h_price,
            monthly=round(h_price * 730, 2),
            source=URL_ARUBA,
            note="Memory Optimized"
        ))

    # 4. Storage Block & Object
    records.append({
        "provider": "Aruba Cloud",
        "region": "IT-Arezzo/Bergamo",
        "kind": "storage",
        "sku": "Cloud Block Storage (SSD)",
        "unit": "EUR/GB/mese",
        "price": 0.05,
        "source": URL_ARUBA
    })
    records.append({
        "provider": "Aruba Cloud",
        "region": "IT-Arezzo/Bergamo",
        "kind": "storage",
        "sku": "Object Storage S3",
        "unit": "EUR/GB/mese",
        "price": 0.01,
        "source": URL_ARUBA
    })

    # 5. Colocation / Housing
    records.append({
        "provider": "Aruba Cloud",
        "region": "IT-Arezzo/Bergamo",
        "kind": "colocation",
        "sku": "Colocation 1U Rack Unit + 300W Power",
        "unit": "EUR/mese",
        "price": 45.00,
        "source": "https://www.arubaperimprese.it/",
        "note": "Spazio 1U in Data Center Bergamo IT3"
    })
    records.append({
        "provider": "Aruba Cloud",
        "region": "IT-Arezzo/Bergamo",
