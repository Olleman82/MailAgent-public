from auth.google_auth import _get_credentials
from config import PROFILES

def setup_all_accounts():
    print("Starting multi-account setup...")
    print("You will be prompted to log in for each account in your browser.")
    
    for profile_name in PROFILES.keys():
        print(f"\n[{profile_name.upper()}] Checking credentials...")
        try:
            # forcing authentication flow if needed by accessing it
            _get_credentials(profile=profile_name)
            print(f" -> Success! {profile_name} is authenticated.")
        except Exception as e:
            print(f" -> Error setting up {profile_name}: {e}")

    print("\nAll done! You can now close this window.")

if __name__ == "__main__":
    setup_all_accounts()
