#### warning, python3's print won't send bytes
##### send arg
r $(python -c "print('A' * 216)")

##### input stdin
r < <(python -c "print('A' * 216)")


##### send bytes with python3 
r $(python -c "import sys; sys.stdout.buffer.write(b'A' * 268 + b'\xef\xbe\xad\xde')")