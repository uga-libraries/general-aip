import os
import subprocess
import configuration as c

os.chdir("insert-path")

for file in os.listdir('.'):
    output = subprocess.run(f'"{c.MD5DEEP}" -br "{file}"', stdout=subprocess.PIPE, shell=True)

    # output.stdout examples:
    # b'cc718d405152d09e307e14b283fa3e77  Anti-Oppressive Facilitation _ Making Meetings Awesome for Everyone_2014.pdf\r\n'
    # b'4e43d17407a04e7a682e122a257a21ae  Digital Preservation Ethos_2021.pdf\r\n'

    # Blank line between each row.
    m0 = os.path.join(f"../aips-to-ingest", f"manifest_default.txt")
    with open(m0, 'a', encoding='utf-8') as m0file:
        m0file.write(output.stdout.decode("UTF-8"))

    # Blank line between each row.
    m1 = os.path.join(f"../aips-to-ingest", f"manifest_no_r.txt")
    with open(m1, 'a', encoding='utf-8') as m1file:
        m1file.write(output.stdout.decode("UTF-8").rstrip("\r"))

    # No blank line. Causes error in ARCHive unless copy to a new text file manually.
    m2 = os.path.join(f"../aips-to-ingest", f"manifest_no_n.txt")
    with open(m2, 'a', encoding='utf-8') as m2file:
        m2file.write(output.stdout.decode("UTF-8").rstrip("\n"))

    # Everything is merged to a single line.
    m3 = os.path.join(f"../aips-to-ingest", f"manifest_no_nr.txt")
    with open(m3, 'a', encoding='utf-8') as m3file:
        m3file.write(output.stdout.decode("UTF-8").rstrip("\r\n"))

    # No blank link. ARCHive can read this. Want something simpler though?
    m4 = os.path.join(f"../aips-to-ingest", f"manifest_add n back.txt")
    with open(m4, 'a', encoding='utf-8') as m4file:
        m4file.write(output.stdout.decode("UTF-8").rstrip("\r\n") + "\n")

