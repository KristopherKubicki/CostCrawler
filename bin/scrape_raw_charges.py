from func import facility

def main():
    # Get all facilities
    all_facilities = facility.get_all_facilities()

    # Iterate over all facilities
    for fac in all_facilities:
        # Scrape each facility
        facility.scrape_facility(fac)

if __name__ == "__main__":
    main()

