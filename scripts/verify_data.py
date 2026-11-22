import sqlite3

conn = sqlite3.connect('subro_recover.db')
prios = dict(conn.execute('SELECT priority_level, count(*) FROM recovery_assessments GROUP BY priority_level').fetchall())
print('Priorities:', prios)

stats = dict(conn.execute('SELECT subrogation_status, count(*) FROM insurance_claims GROUP BY subrogation_status').fetchall())
print('Statuses:', stats)

row = conn.execute("""
    SELECT count(c.claim_id), sum(c.paid_amount), sum(a.net_recovery_estimate),
           sum(CASE WHEN c.subrogation_status = 'Closed Recovered' THEN a.net_recovery_estimate ELSE 0 END)
    FROM insurance_claims c
    JOIN recovery_assessments a ON c.claim_id = a.claim_id
""").fetchone()

print(f"Total claims: {row[0]}")
print(f"Paid exposure: ${row[1]:,.2f}")
print(f"Projected recovery: ${row[2]:,.2f} ({row[2]/row[1]*100:.1f}%)")
print(f"Recovered to date: ${row[3]:,.2f} ({row[3]/row[1]*100:.1f}%)")
