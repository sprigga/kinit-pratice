db = db.getSiblingDB('car');

db.createUser({
  user: 'b-admin',
  pwd: 'Y05os@5352',
  roles: [
    { role: "readWrite", db: "bd-oa" },
    { role: "dbAdmin", db: "bd-oa" }
  ]
});