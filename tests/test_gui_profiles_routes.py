from fastapi.testclient import TestClient

from eve_overview_manager.gui.server import _build_app


def test_gui_profiles_default_root_uses_localappdata(monkeypatch, tmp_path):
    local_app_data = tmp_path / "LocalAppData"
    settings = local_app_data / "CCP" / "EVE" / "c_ccp_eve_tq_tranquility" / "settings_Default"
    settings.mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    client = TestClient(_build_app())

    response = client.get("/api/profiles/default-root")

    assert response.status_code == 200
    assert response.json()["profileRoot"] == str(settings)


def test_gui_profiles_scan_report_and_plan_clone(tmp_path):
    source = tmp_path / "settings_Source"
    target = tmp_path / "settings_Target"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source-user")
    (target / "core_user_1.dat").write_bytes(b"target-user")
    (source / "core_char_456.dat").write_bytes(b"source-char")
    (target / "core_char_456.dat").write_bytes(b"target-char")
    client = TestClient(_build_app())

    scan_response = client.post("/api/profiles/scan", json={"rootPath": str(tmp_path), "resolveNames": False})
    report_response = client.post("/api/profiles/report", json={"profilePath": str(source), "resolveNames": False})
    plan_response = client.post(
        "/api/profiles/plan-clone",
        json={
            "sourcePath": str(source),
            "targetPath": str(target),
            "copyCoreUser": True,
            "copyCoreChar": True,
            "resolveNames": False,
        },
    )

    assert scan_response.status_code == 200
    assert len(scan_response.json()["profiles"]) == 2
    assert report_response.status_code == 200
    assert report_response.json()["report"]["counts"]["coreChar"] == 1
    assert plan_response.status_code == 200
    plan = plan_response.json()["plan"]
    assert plan["blocked"] is False
    assert plan["summary"]["plannedActionCount"] == 2


def test_gui_profiles_backup_execute_and_rollback(tmp_path):
    source = tmp_path / "settings_Source"
    target = tmp_path / "settings_Target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source-user")
    target_file = target / "core_user_1.dat"
    target_file.write_bytes(b"target-user")
    client = TestClient(_build_app())
    plan = client.post(
        "/api/profiles/plan-clone",
        json={"sourcePath": str(source), "targetPath": str(target), "copyCoreUser": True, "resolveNames": False},
    ).json()["plan"]

    backup_response = client.post("/api/profiles/backup-plan", json={"plan": plan, "backupRoot": str(backup_root)})
    manifest = backup_response.json()["backupManifest"]
    execute_response = client.post("/api/profiles/execute-clone", json={"plan": plan, "backupManifest": manifest})
    rollback_response = client.post("/api/profiles/rollback-backup", json={"backupManifest": manifest})

    assert backup_response.status_code == 200
    assert execute_response.status_code == 200
    assert target_file.read_bytes() == b"target-user"
    assert rollback_response.status_code == 200
    assert "rollbackAudit" in rollback_response.json()


def test_gui_profile_package_export_inspect_plan_and_execute(tmp_path):
    source = tmp_path / "settings_Source"
    target = tmp_path / "settings_Target"
    backup_root = tmp_path / "backups"
    package = tmp_path / "transfer.zip"
    source.mkdir()
    target.mkdir()
    (source / "core_char_456.dat").write_bytes(b"source-char")
    target_file = target / "core_char_456.dat"
    target_file.write_bytes(b"target-char")
    client = TestClient(_build_app())

    export_response = client.post(
        "/api/profiles/package/export",
        json={"profilePath": str(source), "packagePath": str(package), "includeCoreChar": True},
    )
    inspect_response = client.post("/api/profiles/package/inspect", json={"packagePath": str(package)})
    plan_response = client.post(
        "/api/profiles/package/plan-import",
        json={"packagePath": str(package), "destinationProfilePath": str(target), "resolveNames": False},
    )
    plan = plan_response.json()["plan"]
    backup_response = client.post("/api/profiles/backup-plan", json={"plan": plan, "backupRoot": str(backup_root)})
    execute_response = client.post(
        "/api/profiles/package/execute-import",
        json={"plan": plan, "backupManifest": backup_response.json()["backupManifest"]},
    )

    assert export_response.status_code == 200
    assert package.exists()
    assert inspect_response.status_code == 200
    assert inspect_response.json()["inspection"]["ok"] is True
    assert plan_response.status_code == 200
    assert plan["blocked"] is False
    assert execute_response.status_code == 200
    assert target_file.read_bytes() == b"source-char"


def test_gui_profile_snapshot_save_and_list(tmp_path):
    profile = tmp_path / "settings_Default"
    library = tmp_path / "snapshots"
    profile.mkdir()
    (profile / "core_char_456.dat").write_bytes(b"source-char")
    client = TestClient(_build_app())

    save_response = client.post(
        "/api/profiles/snapshots/save",
        json={
            "profilePath": str(profile),
            "libraryRoot": str(library),
            "snapshotName": "Known Good",
            "notes": "baseline",
            "includeCoreChar": True,
        },
    )
    list_response = client.post("/api/profiles/snapshots/list", json={"libraryRoot": str(library)})

    assert save_response.status_code == 200
    assert save_response.json()["manifest"]["snapshotName"] == "Known Good"
    assert list_response.status_code == 200
    snapshots = list_response.json()["snapshots"]
    assert len(snapshots) == 1
    assert snapshots[0]["ok"] is True
    assert snapshots[0]["notes"] == "baseline"
