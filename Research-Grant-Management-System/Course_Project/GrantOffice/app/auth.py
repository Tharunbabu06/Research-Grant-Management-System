from . import store

def reset_password(username,password,actor):
 username=username.strip().lower()
 if len(password)<12 or len(password)>200:raise ValueError('Password must contain 12–200 characters.')
 if not store.user(username):raise ValueError('Account not found.')
 with store.connect() as c:
  c.execute('UPDATE users SET password=? WHERE username=?',(store.password_hash(password),username))
  c.execute('DELETE FROM sessions WHERE username=?',(username,))
 store.audit('',actor,'auth.password_reset',{'username':username,'scope':'Password and sessions only; project records preserved.'})
