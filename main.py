from ui.app import NimbusTraderApp
from core.trading_logic import NimbusTraderPlatform

def main():
    platform = NimbusTraderPlatform()
    app = NimbusTraderApp(platform)
    app.mainloop()

if __name__ == "__main__":
    main()