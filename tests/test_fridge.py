def test_get_fridge_empty(client):
    res = client.get("/api/fridge/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_add_ingredient(client):
    res = client.post("/api/fridge/", json={
        "ingredient_name": "番茄",
        "quantity": 3,
        "unit": "顆"
    })
    assert res.status_code == 201
    assert res.json()["action"] in ("created", "updated")

def test_add_then_remove(client):
    # 先新增
    add = client.post("/api/fridge/", json={"ingredient_name": "雞蛋", "amount": 6})
    item_id = add.json().get("id")

    # 再移除
    res = client.delete(f"/api/fridge/{item_id}")
    assert res.status_code == 200

def test_remove_nonexistent(client):
    res = client.delete("/api/fridge/99999")
    assert res.status_code == 404