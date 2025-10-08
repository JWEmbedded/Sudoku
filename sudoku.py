import tkinter as tk
from tkinter import messagebox
import random
import copy

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("스도쿠 게임")
        self.root.resizable(False, False)
        
        self.board = [[0]*9 for _ in range(9)]
        self.solution = [[0]*9 for _ in range(9)]
        self.cells = [[None]*9 for _ in range(9)]
        self.memo_frames = [[None]*9 for _ in range(9)]
        self.memo_labels = [[None]*9 for _ in range(9)]
        self.memos = [[set() for _ in range(9)] for _ in range(9)]
        self.selected = None
        self.memo_mode = False
        self.highlighted_number = None
        self.number_buttons = {}
        self.difficulty = 'medium'
        
        self.create_widgets()
        self.new_game()
    
    def create_widgets(self):
        # 상단 버튼 프레임
        btn_frame = tk.Frame(self.root, bg='#2c3e50')
        btn_frame.pack(pady=10)
        
        # 난이도 표시 프레임
        difficulty_frame = tk.Frame(self.root, bg='#2c3e50')
        difficulty_frame.pack(pady=5)
        
        tk.Label(difficulty_frame, text="난이도: 보통", bg='#2c3e50', fg='white',
                font=('Arial', 11, 'bold')).pack(padx=5)
        
        tk.Button(btn_frame, text="새 게임", command=self.new_game, 
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="정답 확인", command=self.check_solution,
                 bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'),
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        self.memo_btn = tk.Button(btn_frame, text="메모 모드", command=self.toggle_memo_mode,
                 bg='#95a5a6', fg='white', font=('Arial', 12, 'bold'),
                 padx=10, pady=5)
        self.memo_btn.pack(side=tk.LEFT, padx=5)
        
        # 스도쿠 보드 프레임
        board_frame = tk.Frame(self.root, bg='#34495e', bd=3, relief=tk.RAISED)
        board_frame.pack(padx=20, pady=10)
        
        # 9x9 셀 생성
        for i in range(9):
            for j in range(9):
                # 3x3 박스 경계 강조
                padx = (0, 3) if j % 3 == 2 and j != 8 else (0, 1)
                pady = (0, 3) if i % 3 == 2 and i != 8 else (0, 1)
                
                frame = tk.Frame(board_frame, 
                               highlightbackground='#34495e',
                               highlightthickness=1,
                               width=80, height=80)
                frame.grid(row=i, column=j, padx=padx, pady=pady)
                frame.grid_propagate(False)
                
                # 일반 입력 셀
                cell = tk.Entry(frame, width=3, font=('Arial', 28, 'bold'),
                              justify='center', bg='white', bd=0)
                cell.place(relx=0.5, rely=0.5, anchor='center')
                cell.bind('<FocusIn>', lambda e, r=i, c=j: self.cell_selected(r, c))
                cell.bind('<Key>', lambda e, r=i, c=j: self.on_key_press(e, r, c))
                cell.bind('<Button-1>', lambda e, r=i, c=j: self.cell_clicked(r, c))
                self.cells[i][j] = cell
                
                # 메모용 3x3 그리드
                memo_frame = tk.Frame(frame, bg='white')
                memo_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
                
                for mi in range(3):
                    memo_frame.grid_rowconfigure(mi, weight=1)
                    memo_frame.grid_columnconfigure(mi, weight=1)
                
                for mi in range(3):
                    for mj in range(3):
                        lbl = tk.Label(memo_frame, text='', 
                                     font=('Arial', 12, 'bold'), 
                                     bg='white', fg='#7f8c8d')
                        lbl.grid(row=mi, column=mj, sticky='nsew')
                
                memo_frame.place_forget()
                self.memo_frames[i][j] = memo_frame
                self.memo_labels[i][j] = memo_frame.winfo_children()
        
        # 숫자 버튼 프레임
        num_frame = tk.Frame(self.root, bg='#2c3e50')
        num_frame.pack(pady=10)
        
        for num in range(1, 10):
            btn = tk.Button(num_frame, text=str(num), command=lambda n=num: self.insert_number(n),
                     bg='#95a5a6', font=('Arial', 16, 'bold'),
                     width=3, height=1)
            btn.pack(side=tk.LEFT, padx=3)
            self.number_buttons[num] = btn
        
        tk.Button(num_frame, text="지우기", command=lambda: self.insert_number(0),
                 bg='#e74c3c', fg='white', font=('Arial', 14, 'bold'),
                 padx=10).pack(side=tk.LEFT, padx=3)
    
    def toggle_memo_mode(self):
        self.memo_mode = not self.memo_mode
        if self.memo_mode:
            self.memo_btn.config(bg='#f39c12', text="메모 모드 (ON)")
        else:
            self.memo_btn.config(bg='#95a5a6', text="메모 모드")
    
    def cell_clicked(self, row, col):
        # 클릭한 셀의 숫자 가져오기
        cell_value = self.cells[row][col].get()
        
        if cell_value and cell_value.isdigit():
            clicked_num = int(cell_value)
            
            # 같은 숫자를 다시 클릭하면 하이라이트 해제
            if self.highlighted_number == clicked_num:
                self.highlighted_number = None
            else:
                self.highlighted_number = clicked_num
            
            self.update_highlights()
    
    def update_highlights(self):
        # 모든 셀의 배경색 업데이트
        for i in range(9):
            for j in range(9):
                cell_value = self.cells[i][j].get()
                is_disabled = self.cells[i][j].cget('state') == 'disabled'
                
                # 기본 배경색 결정
                if is_disabled:
                    base_color = '#ecf0f1'
                elif self.selected == (i, j):
                    base_color = '#3498db'
                else:
                    base_color = 'white'
                
                # 하이라이트된 숫자와 일치하면 노란색으로
                if (self.highlighted_number and cell_value and 
                    cell_value.isdigit() and int(cell_value) == self.highlighted_number):
                    if is_disabled:
                        self.cells[i][j].config(disabledbackground='#fff59d')
                    else:
                        self.cells[i][j].config(bg='#fff59d')
                else:
                    if is_disabled:
                        self.cells[i][j].config(disabledbackground=base_color)
                    else:
                        self.cells[i][j].config(bg=base_color)
        
        # 숫자 버튼 상태 업데이트
        self.update_number_buttons()
    
    def update_number_buttons(self):
        # 각 숫자가 보드에 몇 개 사용되었는지 카운트
        for num in range(1, 10):
            count = 0
            for i in range(9):
                for j in range(9):
                    cell_value = self.cells[i][j].get()
                    if cell_value and cell_value.isdigit() and int(cell_value) == num:
                        count += 1
            
            # 9개 모두 사용되었으면 버튼 숨기기
            if count >= 9:
                self.number_buttons[num].pack_forget()
            else:
                # 숨겨진 버튼이 있다면 다시 표시
                if not self.number_buttons[num].winfo_ismapped():
                    # 올바른 순서로 다시 배치
                    self.repack_number_buttons()
                    break
    
    def repack_number_buttons(self):
        # 모든 숫자 버튼을 올바른 순서로 다시 배치
        for num in range(1, 10):
            count = 0
            for i in range(9):
                for j in range(9):
                    cell_value = self.cells[i][j].get()
                    if cell_value and cell_value.isdigit() and int(cell_value) == num:
                        count += 1
            
            if count < 9:
                self.number_buttons[num].pack(side=tk.LEFT, padx=3)
    
    def cell_selected(self, row, col):
        self.selected = (row, col)
        self.update_highlights()
    
    def on_key_press(self, event, row, col):
        if event.char in '123456789':
            self.insert_number(int(event.char))
            return 'break'
        elif event.keysym in ('BackSpace', 'Delete'):
            self.insert_number(0)
            return 'break'
    
    def insert_number(self, num):
        if not self.selected or self.cells[self.selected[0]][self.selected[1]].cget('state') != 'normal':
            return
        
        r, c = self.selected
        
        if self.memo_mode:
            # 메모 모드
            if num == 0:
                # 모든 메모 지우기
                self.memos[r][c].clear()
                self.update_memo_display(r, c)
            else:
                # 메모 토글
                if num in self.memos[r][c]:
                    self.memos[r][c].remove(num)
                else:
                    self.memos[r][c].add(num)
                self.update_memo_display(r, c)
        else:
            # 일반 모드
            if num == 0:
                self.cells[r][c].delete(0, tk.END)
                self.board[r][c] = 0
                self.cells[r][c].place(relx=0.5, rely=0.5, anchor='center')
                self.memo_frames[r][c].place_forget()
            else:
                # 메모 지우기
                self.memos[r][c].clear()
                self.memo_frames[r][c].place_forget()
                
                self.cells[r][c].delete(0, tk.END)
                self.cells[r][c].insert(0, str(num))
                self.cells[r][c].place(relx=0.5, rely=0.5, anchor='center')
                self.board[r][c] = num
                
                if not self.is_valid(r, c, num):
                    self.cells[r][c].config(fg='red')
                else:
                    self.cells[r][c].config(fg='blue')
        
        self.update_highlights()
    
    def update_memo_display(self, row, col):
        if self.memos[row][col]:
            # 메모가 있으면 Entry 숨기고 메모 표시
            self.cells[row][col].place_forget()
            self.memo_frames[row][col].place(relx=0, rely=0, relwidth=1, relheight=1)
            
            # 각 위치에 숫자 표시 (1-9)
            for idx, label in enumerate(self.memo_labels[row][col]):
                num = idx + 1
                if num in self.memos[row][col]:
                    label.config(text=str(num))
                else:
                    label.config(text='')
        else:
            # 메모가 없으면 Entry 표시
            self.cells[row][col].place(relx=0.5, rely=0.5, anchor='center')
            self.memo_frames[row][col].place_forget()
    
    def is_valid(self, row, col, num):
        # 행 체크
        for j in range(9):
            if j != col and self.board[row][j] == num:
                return False
        
        # 열 체크
        for i in range(9):
            if i != row and self.board[i][col] == num:
                return False
        
        # 3x3 박스 체크
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i, j) != (row, col) and self.board[i][j] == num:
                    return False
        
        return True
    
    def generate_solution(self):
        # 빈 보드에서 시작
        board = [[0]*9 for _ in range(9)]
        
        def solve(board):
            for i in range(9):
                for j in range(9):
                    if board[i][j] == 0:
                        nums = list(range(1, 10))
                        random.shuffle(nums)
                        for num in nums:
                            if self.is_valid_for_board(board, i, j, num):
                                board[i][j] = num
                                if solve(board):
                                    return True
                                board[i][j] = 0
                        return False
            return True
        
        solve(board)
        return board
    
    def is_valid_for_board(self, board, row, col, num):
        for j in range(9):
            if board[row][j] == num:
                return False
        for i in range(9):
            if board[i][col] == num:
                return False
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False
        return True
    
    def new_game(self):
        # 해답 생성
        self.solution = self.generate_solution()
        self.board = copy.deepcopy(self.solution)
        
        # 보통 난이도: 43개 제거
        cells_to_remove = 43
        
        removed = 0
        while removed < cells_to_remove:
            i, j = random.randint(0, 8), random.randint(0, 8)
            if self.board[i][j] != 0:
                self.board[i][j] = 0
                removed += 1
        
        # 메모 초기화
        self.memos = [[set() for _ in range(9)] for _ in range(9)]
        
        # UI 업데이트
        for i in range(9):
            for j in range(9):
                self.cells[i][j].config(state='normal', bg='white', fg='black')
                self.cells[i][j].delete(0, tk.END)
                self.memo_frames[i][j].place_forget()
                self.cells[i][j].place(relx=0.5, rely=0.5, anchor='center')
                
                if self.board[i][j] != 0:
                    self.cells[i][j].insert(0, str(self.board[i][j]))
                    self.cells[i][j].config(state='disabled', 
                                          disabledforeground='black',
                                          disabledbackground='#ecf0f1')
    
    def check_solution(self):
        for i in range(9):
            for j in range(9):
                try:
                    val = int(self.cells[i][j].get()) if self.cells[i][j].get() else 0
                    if val != self.solution[i][j]:
                        messagebox.showinfo("결과", "아직 완성되지 않았거나 오류가 있습니다!")
                        return
                except:
                    messagebox.showinfo("결과", "모든 칸을 채워주세요!")
                    return
        
        messagebox.showinfo("축하합니다!", "스도쿠를 완성했습니다! 🎉")

if __name__ == "__main__":
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()