db = db.getSiblingDB('bd-oa');

db.createUser({
  user: 'oa-admin',
  pwd: 'Bdfrost168',
  roles: [
    { role: "readWrite", db: "bd-oa" },
    { role: "dbAdmin", db: "bd-oa" }
  ]
});