from ui.app import StopLossApp
from core.trading_logic import StopLossPlatform

def main():
    platform = StopLossPlatform()
    app = StopLossApp(platform)
    app.mainloop()

if __name__ == "__main__":
    main()