import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.moofile_util import MooFileUtil


def print_check(name, actual, expected):
    """Print a readable validation result and return whether it passed."""
    passed = actual == expected
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: actual={actual!r}, expected={expected!r}")
    return passed


def create_test_records(total=30):
    """Create regular-table records for CRUD testing."""
    return [
        {
            "name": f"user-{index:02d}",
            "email": f"user-{index:02d}@example.com",
            "age": 20 + index,
            "role": "admin" if index % 5 == 0 else "user",
        }
        for index in range(total)
    ]


def test_regular_table_crud():
    """Run create, read, update, and delete operations on a regular table."""
    print("\n=== Regular table CRUD test ===")
    checks = []

    with tempfile.TemporaryDirectory() as temp_dir:
        util = MooFileUtil(temp_dir)
        table_name = "users"
        indexes = ["email", "role"]

        database_path = util.create_database(table_name)
        print(f"Database created: {database_path}")
        checks.append(print_check("database exists", util.database_exists(table_name), True))

        records = create_test_records()
        util.insert_data(table_name, records, indexes)
        checks.append(print_check("insert count", util.count_data(table_name, {}, indexes), 30))

        admins = util.query_data(table_name, {"role": "admin"}, indexes)
        checks.append(print_check("admin query count", len(admins), 6))
        print(f"Admin sample: {admins[:2]}")

        util.update_data(table_name, {"role": "user"}, {"status": "active"}, indexes)
        active_count = util.count_data(table_name, {"status": "active"}, indexes)
        checks.append(print_check("updated user count", active_count, 24))

        util.delete_data(table_name, {"age": {"$lt": 25}}, indexes)
        checks.append(print_check("count after delete", util.count_data(table_name, {}, indexes), 25))

        util.copy_database(table_name, "users_copy")
        checks.append(print_check("copy exists", util.database_exists("users_copy"), True))

        util.rename_database("users_copy", "users_archive")
        checks.append(print_check("renamed database exists", util.database_exists("users_archive"), True))

        util.delete_database("users_archive")
        checks.append(print_check("archive deleted", util.database_exists("users_archive"), False))
        print(f"Remaining databases: {util.list_databases()}")

    passed = all(checks)
    print(f"\nRegular table result: {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    if not test_regular_table_crud():
        raise SystemExit(1)
