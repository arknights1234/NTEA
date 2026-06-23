import sys
from gui import MainGUI

def main():
    print("시작")
    
    try:
        app = MainGUI()
        
        app.mainloop()
        
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
    finally:
        print("종료")

if __name__ == "__main__":
    main()