import sqlalchemy

from models.users import users_table

metadata = sqlalchemy.MetaData()


posts_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey(users_table.c.id)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime()),
    sqlalchemy.Column("title", sqlalchemy.String(100)),
    sqlalchemy.Column("content", sqlalchemy.Text()),
)

like_table = sqlalchemy.Table(
    "like",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("like", sqlalchemy.Boolean),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey(posts_table.c.id)),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey(users_table.c.id))
)
