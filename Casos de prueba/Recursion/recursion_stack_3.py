def rec_stack(n):
    if n > 0:
        print("In:", n)
    if n == 0:
        return
    rec_stack(n - 1)
    print("Out:", n)

rec_stack(2)