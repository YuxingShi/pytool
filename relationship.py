# coding:utf-8

from py2neo import Graph, Node, Relationship

graph = Graph()
a = Node("Person", name="Alice")
b = Node("Person", name="Bob")
ab = Relationship(a, "KNOWS", b)
print(ab)
