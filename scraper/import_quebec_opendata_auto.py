"""
Import automatique (sans confirmation interactive) des événements Québec.
"""
import sys
sys.path.insert(0, '.')

from import_quebec_opendata import (
    fetch_montreal_events, deduplicate_with_existing, import_events
)

if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT ÉVÉNEMENTS QUÉBEC - OPEN DATA (CC-BY 4.0)")
    print("=" * 60)
    
    # Montréal
    print("\nSOURCE: Ville de Montréal (CC-BY 4.0)")
    mtl_events = fetch_montreal_events()
    
    if mtl_events:
        # Stats
        cat_counts = {}
        for e in mtl_events:
            for c in e["categories"]:
                cat_counts[c] = cat_counts.get(c, 0) + 1
        
        print(f"\nCatégories:")
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:15]:
            print(f"  {cat}: {count}")
        
        # Déduplications
        unique_events = deduplicate_with_existing(mtl_events)
        
        if unique_events:
            print(f"\nAperçu (5 premiers):")
            for e in unique_events[:5]:
                print(f"  {e['date']} | {e['title'][:60]}")
                print(f"     {e['location'][:60]}")
                print(f"     {e['categories']}")
                print(f"     {e['source_url'][:80]}")
                print()
            
            # Import automatique
            print(f"\nIMPORT de {len(unique_events)} événements...")
            import_events(unique_events, "Montréal Open Data")
        else:
            print("\nAucun nouvel événement à importer.")
    
    print("\nTerminé!")
