import csv
import json
import subprocess
import sys
from pathlib import Path


OWNER = "rgap"
REPO = "Coolbox-B2B-WebApp"
FULL_REPO = f"{OWNER}/{REPO}"
PROJECT_TITLE = "Coolbox B2B WebApp"
CSV_PATH = Path("user_stories.csv")
COLUMNS = ["Product Backlog", "To Do", "In Progress", "Testing", "Done"]
INITIAL_STATUS = "Product Backlog"
COLUMN_COLORS = ["GRAY", "BLUE", "YELLOW", "ORANGE", "GREEN"]
BOARD_VIEW_NAME = "Tablero Kanban"
WIP_LIMITS = {
    "To Do": 5,
    "In Progress": 3,
    "Testing": 3,
}


def gh(args, check=True):
    command = ["gh", *args]
    result = subprocess.run(command, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)

    return result


def gh_graphql(query, variables):
    result = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=json.dumps({"query": query, "variables": variables}),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)

    return json.loads(result.stdout or "{}")


def gh_json(args):
    output = gh(args).stdout.strip()
    return json.loads(output or "[]")


def projects_by_title():
    projects = gh_json([
        "project",
        "list",
        "--owner",
        OWNER,
        "--format",
        "json",
        "--limit",
        "100",
    ]).get("projects", [])

    return [project for project in projects if project["title"] == PROJECT_TITLE]


def read_rows():
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def labels_from(row):
    raw_labels = row.get("Etiquetas (labels)", "")
    return [
        label.strip()
        for label in raw_labels.replace(";", ",").split(",")
        if label.strip()
    ]


def issue_body(row):
    sections = []

    for column, value in row.items():
        value = (value or "").strip()
        if column in ["Titulo", "Etiquetas (labels)"] or not value:
            continue
        sections.append(f"## {column}\n\n{value}")

    sections.append(f"_Importado desde `{CSV_PATH.name}`._")
    return "\n\n".join(sections)


def ensure_repo():
    if gh(["repo", "view", FULL_REPO], check=False).returncode == 0:
        print(f"Repo existente: {FULL_REPO}")
        gh([
            "repo",
            "edit",
            FULL_REPO,
            "--visibility",
            "public",
            "--accept-visibility-change-consequences",
        ])
        return

    print(f"Creando repo: {FULL_REPO}")
    gh([
        "repo",
        "create",
        FULL_REPO,
        "--public",
        "--description",
        "MVP del CRM B2B post-venta para Coolbox.",
    ])


def delete_existing_repo():
    if gh(["repo", "view", FULL_REPO], check=False).returncode != 0:
        return

    print(f"Borrando repo existente: {FULL_REPO}")
    gh(["repo", "delete", FULL_REPO, "--yes"])


def delete_existing_projects():
    for project in projects_by_title():
        print(f"Borrando Project existente: {PROJECT_TITLE} (#{project['number']})")
        gh_graphql(
            """
            mutation($projectId: ID!) {
              deleteProjectV2(input: { projectId: $projectId }) {
                clientMutationId
              }
            }
            """,
            {"projectId": project["id"]},
        )


def project_owner_and_repo_ids():
    data = gh_graphql(
        """
        query($owner: String!, $repo: String!) {
          repositoryOwner(login: $owner) {
            id
          }
          repository(owner: $owner, name: $repo) {
            id
          }
        }
        """,
        {
            "owner": OWNER,
            "repo": REPO,
        },
    )
    owner = data["data"]["repositoryOwner"]
    repository = data["data"]["repository"]

    if not owner:
        raise SystemExit(f"No existe el owner de GitHub: {OWNER}.")

    if not repository:
        raise SystemExit(f"No existe el repo de GitHub: {FULL_REPO}.")

    return owner["id"], repository["id"]


def project():
    print(f"Creando Project: {PROJECT_TITLE}")
    owner_id, repository_id = project_owner_and_repo_ids()
    created = gh_graphql(
        """
        mutation($ownerId: ID!, $title: String!, $repositoryId: ID!) {
          createProjectV2(input: {
            ownerId: $ownerId,
            title: $title,
            repositoryId: $repositoryId
          }) {
            projectV2 {
              number
            }
          }
        }
        """,
        {
            "ownerId": owner_id,
            "title": PROJECT_TITLE,
            "repositoryId": repository_id,
        },
    )
    number = created["data"]["createProjectV2"]["projectV2"]["number"]

    return gh_json([
        "project",
        "view",
        str(number),
        "--owner",
        OWNER,
        "--format",
        "json",
    ])


def link_project(number):
    gh([
        "project",
        "link",
        str(number),
        "--owner",
        OWNER,
        "--repo",
        REPO,
    ], check=False)


def make_project_public(number):
    gh([
        "project",
        "edit",
        str(number),
        "--owner",
        OWNER,
        "--visibility",
        "PUBLIC",
    ])


def project_view_names(project_number):
    data = gh_graphql(
        """
        query($owner: String!, $number: Int!) {
          user(login: $owner) {
            projectV2(number: $number) {
              views(first: 20) {
                nodes {
                  name
                }
              }
            }
          }
        }
        """,
        {
            "owner": OWNER,
            "number": project_number,
        },
    )
    views = data["data"]["user"]["projectV2"]["views"]["nodes"]
    return {view["name"] for view in views}


def create_project_view(project_number, name, layout):
    print(f"Creando vista {name}: {layout}")
    gh([
        "api",
        "-X",
        "POST",
        f"users/{OWNER}/projectsV2/{project_number}/views",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2026-03-10",
        "-f",
        f"name={name}",
        "-f",
        f"layout={layout}",
        "-f",
        "filter=is:issue",
    ])


def ensure_project_views(project_number):
    views = project_view_names(project_number)

    if BOARD_VIEW_NAME not in views:
        create_project_view(project_number, BOARD_VIEW_NAME, "board")


def status_field(project_number):
    fields = gh_json([
        "project",
        "field-list",
        str(project_number),
        "--owner",
        OWNER,
        "--format",
        "json",
        "--limit",
        "50",
    ]).get("fields", [])

    for field in fields:
        if field["name"] == "Status":
            return field

    return None


def project_columns():
    return [status_display_name(name) for name in COLUMNS]


def status_display_name(name):
    if name in WIP_LIMITS:
        return f"{name} (WIP {WIP_LIMITS[name]})"

    return name


def legacy_column_name(name):
    return f"{name} [{WIP_LIMITS[name]}]" if name in WIP_LIMITS else name


def canonical_status_name(name):
    if not name:
        return ""

    if name == "Todo":
        return "To Do"

    for column in COLUMNS:
        if name in [column, status_display_name(column), legacy_column_name(column)]:
            return column

    return name


def existing_option_id(current_options, name):
    candidates = [status_display_name(name), name, legacy_column_name(name)]

    if name == "To Do":
        candidates.append("Todo")

    for candidate in candidates:
        if candidate in current_options:
            return current_options[candidate]

    return None


def status_options(field):
    current_options = {option["name"]: option["id"] for option in field.get("options", [])}

    return [
        {
            **({"id": option_id} if option_id else {}),
            "name": status_display_name(name),
            "color": COLUMN_COLORS[index],
            "description": "",
        }
        for index, name in enumerate(COLUMNS)
        for option_id in [existing_option_id(current_options, name)]
    ]


def update_status_field(field):
    gh_graphql(
        """
        mutation($fieldId: ID!, $options: [ProjectV2SingleSelectFieldOptionInput!]) {
          updateProjectV2Field(input: {
            fieldId: $fieldId,
            singleSelectOptions: $options
          }) {
            projectV2Field {
              ... on ProjectV2SingleSelectField {
                id
              }
            }
          }
        }
        """,
        {
            "fieldId": field["id"],
            "options": status_options(field),
        },
    )


def ensure_columns(project_number):
    field = status_field(project_number)
    current_columns = []

    if field:
        current_columns = [option["name"] for option in field.get("options", [])]

    if current_columns == project_columns():
        print("Columnas del Project listas.")
        return field

    if field:
        print("Actualizando columnas del campo Status.")
        update_status_field(field)
    else:
        print("Creando campo Status con columnas del backlog.")
        gh([
            "project",
            "field-create",
            str(project_number),
            "--owner",
            OWNER,
            "--name",
            "Status",
            "--data-type",
            "SINGLE_SELECT",
            "--single-select-options",
            ",".join(project_columns()),
        ])

    return status_field(project_number)


def status_option_id(field, status_name):
    for option in field.get("options", []):
        if canonical_status_name(option["name"]) == status_name:
            return option["id"]

    raise SystemExit(f"No existe la columna {status_name}.")


def ensure_labels(labels):
    for label in sorted(set(labels)):
        gh([
            "label",
            "create",
            label,
            "--repo",
            FULL_REPO,
            "--color",
            "1D76DB",
            "--force",
        ])


def existing_issues():
    issues = gh_json([
        "issue",
        "list",
        "--repo",
        FULL_REPO,
        "--state",
        "all",
        "--json",
        "title,url",
        "--limit",
        "1000",
    ])
    return {issue["title"]: issue["url"] for issue in issues}


def existing_project_items(project_number):
    items = gh_json([
        "project",
        "item-list",
        str(project_number),
        "--owner",
        OWNER,
        "--format",
        "json",
        "--limit",
        "1000",
    ])
    return {item["title"]: item["id"] for item in items.get("items", [])}


def project_items(project_number):
    return gh_json([
        "project",
        "item-list",
        str(project_number),
        "--owner",
        OWNER,
        "--format",
        "json",
        "--limit",
        "1000",
    ]).get("items", [])


def project_status_counts(project_number):
    counts = {column: 0 for column in COLUMNS}

    for item in project_items(project_number):
        status = canonical_status_name(item.get("status"))

        if status in counts:
            counts[status] += 1

    return counts


def enforce_wip_limit(project_number, item_id, target_status):
    if target_status not in WIP_LIMITS:
        return

    items_in_column = [
        item
        for item in project_items(project_number)
        if item.get("id") != item_id
        and canonical_status_name(item.get("status")) == target_status
    ]
    current_count = len(items_in_column)
    limit = WIP_LIMITS[target_status]

    if current_count >= limit:
        raise SystemExit(
            f"WIP limit alcanzado en '{target_status}': "
            f"{current_count}/{limit}. No se movio el item {item_id}."
        )


def validate_wip_limits(project_number):
    counts = project_status_counts(project_number)

    for status_name, limit in WIP_LIMITS.items():
        count = counts.get(status_name, 0)

        if count > limit:
            raise SystemExit(
                f"WIP limit excedido en '{status_name}': {count}/{limit}."
            )

    summary = ", ".join(
        f"{status_name} {counts.get(status_name, 0)}/{limit}"
        for status_name, limit in WIP_LIMITS.items()
    )
    print(f"WIP limits validados: {summary}.")


def create_issue(row, labels):
    title = row["Titulo"].strip()

    args = [
        "issue",
        "create",
        "--repo",
        FULL_REPO,
        "--title",
        title,
        "--body",
        issue_body(row),
    ]

    if labels:
        args.extend(["--label", ",".join(labels)])

    print(f"Creando issue: {title}")
    return gh(args).stdout.strip()


def add_to_project(project_number, issue_url):
    result = gh([
        "project",
        "item-add",
        str(project_number),
        "--owner",
        OWNER,
        "--url",
        issue_url,
        "--format",
        "json",
    ], check=False)

    if result.returncode == 0:
        print(f"Agregado al Project: {issue_url}")
        return json.loads(result.stdout or "{}").get("id")

    if "already" in result.stderr.lower():
        print(f"Ya estaba en el Project: {issue_url}")
        return None

    print(result.stderr.strip(), file=sys.stderr)
    raise SystemExit(result.returncode)


def move_to_status(project_data, status, item_id, status_name):
    enforce_wip_limit(project_data["number"], item_id, status_name)
    gh([
        "project",
        "item-edit",
        "--id",
        item_id,
        "--project-id",
        project_data["id"],
        "--field-id",
        status["id"],
        "--single-select-option-id",
        status_option_id(status, status_name),
    ])


def move_to_initial_status(project_data, status, item_id):
    move_to_status(project_data, status, item_id, INITIAL_STATUS)


def main():
    rows = read_rows()
    print(f"User stories leidas: {len(rows)}")

    delete_existing_projects()
    delete_existing_repo()

    ensure_repo()
    project_data = project()
    make_project_public(project_data["number"])
    link_project(project_data["number"])
    status = ensure_columns(project_data["number"])
    ensure_project_views(project_data["number"])

    all_labels = [label for row in rows for label in labels_from(row)]
    ensure_labels(all_labels)

    issues_by_title = existing_issues()
    items_by_title = existing_project_items(project_data["number"])

    for row in rows:
        title = row["Titulo"].strip()
        labels = labels_from(row)
        issue_url = issues_by_title.get(title) or create_issue(row, labels)
        item_id = items_by_title.get(title)

        if not item_id:
            item_id = add_to_project(project_data["number"], issue_url)

        if item_id:
            move_to_initial_status(project_data, status, item_id)

    validate_wip_limits(project_data["number"])
    print("GitHub Project poblado.")


if __name__ == "__main__":
    main()
