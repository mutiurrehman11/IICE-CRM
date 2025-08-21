from datetime import date

single_due_date = date(2025, 8, 20)
installments_count = 3
final_installment_date = single_due_date

print(f'Start date: {final_installment_date}')

for i in range(installments_count - 1):
    if final_installment_date.month < 12:
        final_installment_date = final_installment_date.replace(month=final_installment_date.month + 1)
    else:
        final_installment_date = final_installment_date.replace(year=final_installment_date.year + 1, month=1)
    print(f'Installment {i+2}: {final_installment_date}')

print(f'Final installment date: {final_installment_date}')
session_end = date(2025, 11, 13)
print(f'Session end date: {session_end}')
print(f'Final > Session end: {final_installment_date > session_end}')