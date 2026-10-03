"""The inspector has to answer in the rules' own units, or it makes things worse.

Two numbers for one face is a reconciliation the agent then has to do by hand, which is
the cost this command exists to remove. So the assertions here are mostly agreements:
the droop this prints is the angle the overhang rule fired on, and the face this
attributes a finding to is the face the rule measured.
"""

from build123d import Box, Pos
import pytest

from nurb import probe
from nurb.checks import Context, concave_edges, run


def test_droop_is_the_number_the_overhang_rule_reports():
    """A flat ceiling: the rule says 90 degrees, so the face table has to say 90 too."""
    shape = Box(6, 6, 20) + Pos(0, 0, 12) * Box(30, 30, 4)
    ctx = Context()
    finding = next(f for f in run(shape, ctx, only={"overhang"}))
    rows, _ = probe.faces(shape, ctx)
    row = probe._on_face(rows, finding.where)
    assert row is not None
    assert row["droop"] == pytest.approx(finding.value)
    assert row["droop"] == pytest.approx(90.0)


def test_a_finding_resolves_to_a_face_whose_centre_is_not_on_it():
    """The cap underside is an annulus, so its centroid sits in the hole.

    Containment alone misses this, and it is not an exotic shape: it is every plate
    with a pocket in it. Matching the centre the rule recorded is what recovers it.
    """
    shape = Box(6, 6, 20) + Pos(0, 0, 12) * Box(30, 30, 4)
    ctx = Context()
    finding = next(f for f in run(shape, ctx, only={"overhang"}))
    rows, _ = probe.faces(shape, ctx)
    row = probe._on_face(rows, finding.where)
    assert row["area"] == pytest.approx(30 * 30 - 6 * 6)
    assert row["center"].Z == pytest.approx(10.0)


def test_a_centre_of_mass_resolves_to_no_face_at_all():
    """Stability's `where` is not on the solid's surface.

    Nearest-centre matching answers this one with a confident, meaningless face, which
    is worse than an empty line: the agent would go and edit it.
    """
    shape = Box(4, 4, 40) + Pos(30, 0, 18) * Box(56, 4, 4)
    ctx = Context()
    finding = next(f for f in run(shape, ctx, only={"stability"}))
    rows, _ = probe.faces(shape, ctx)
    assert probe._on_face(rows, finding.where) is None


def test_faces_come_back_largest_first_with_the_bed_marked():
    shape = Box(40, 30, 2)
    ctx = Context()
    rows, bed = probe.faces(shape, ctx)
    assert bed == pytest.approx(-1.0)
    assert [r["area"] for r in rows] == sorted((r["area"] for r in rows), reverse=True)
    grounded = [r for r in rows if r["grounded"]]
    assert len(grounded) == 1
    assert grounded[0]["center"].Z == pytest.approx(-1.0)


def test_the_bed_face_is_a_90_degree_droop_that_is_not_a_finding():
    """Why the table and the findings can disagree, spelled out rather than inferred.

    Every part's bottom face reads as a 90 degree overhang and none of them is one. An
    inspector that hid the number would leave the agent unable to tell this face from a
    real ceiling; one that printed it without the note invites a fix to a non-problem.
    """
    shape = Box(40, 30, 2)
    ctx = Context()
    rows, _ = probe.faces(shape, ctx)
    bottom = next(r for r in rows if r["grounded"])
    assert bottom["droop"] == pytest.approx(90.0)
    assert run(shape, ctx, only={"overhang"}) == []
    assert "on the bed" in probe._face_line(bottom)


def test_report_names_the_droop_convention():
    """The units are the whole contract, so they are stated in the output."""
    shape = Box(40, 30, 2)
    ctx = Context()
    text = "\n".join(probe.report("thing", shape, ctx, run(shape, ctx)))
    assert "droop" in text
    assert "build direction" in text
    assert "0 is a wall" in text


def test_axis_aligned_normals_get_a_label_and_the_rest_get_numbers():
    shape = Box(10, 10, 10)
    ctx = Context()
    rows, _ = probe.faces(shape, ctx)
    labels = {probe._label(r["normal"]) for r in rows}
    assert labels == {"+X", "-X", "+Y", "-Y", "+Z", "-Z"}


def test_no_negative_zero_in_the_droop_column():
    """A vertical wall is 0 degrees, and `-0.0` reads as a bug in the tool."""
    shape = Box(10, 10, 10)
    ctx = Context()
    rows, _ = probe.faces(shape, ctx)
    wall = next(r for r in rows if abs(r["droop"]) < 0.05)
    assert "-0.0" not in probe._face_line(wall)


def test_face_pick_names_the_face_a_click_lands_on():
    shape = Box(40, 30, 2)
    ctx = Context()
    rows, _ = probe.faces(shape, ctx)
    top = next(r for r in rows if probe._label(r["normal"]) == "+Z")
    pick = probe.resolve_pick(shape, ctx, "face", top["center"])
    assert pick is not None
    assert pick["mode"] == "face"
    assert pick["area"] == pytest.approx(40 * 30, abs=0.1)
    assert pick["normal"] == "+Z"
    assert pick["triangles"]  # highlight mesh for the viewer
    assert "face I selected" in probe.format_pick_reference("plate", pick)


def test_face_pick_refuses_a_point_in_empty_space():
    shape = Box(10, 10, 10)
    ctx = Context()
    assert probe.resolve_pick(shape, ctx, "face", (100.0, 100.0, 100.0)) is None


def test_edge_pick_names_the_nearest_edge():
    shape = Box(20, 20, 20)
    ctx = Context()
    # Midpoint of the top +Y edge of a centered box: (0, 10, 10).
    pick = probe.resolve_pick(shape, ctx, "edge", (0.0, 10.0, 10.0))
    assert pick is not None
    assert pick["mode"] == "edge"
    assert pick["length"] == pytest.approx(20.0)
    assert pick["line"] is not None
    assert "edge I selected" in probe.format_pick_reference("cube", pick)


def test_edge_pick_refuses_a_point_far_from_every_edge():
    shape = Box(10, 10, 10)
    ctx = Context()
    assert probe.resolve_pick(shape, ctx, "edge", (100.0, 100.0, 100.0)) is None


def test_point_pick_echoes_the_click():
    shape = Box(10, 10, 10)
    ctx = Context()
    pick = probe.resolve_pick(shape, ctx, "point", (1.234, -2.5, 3.01))
    assert pick == {"mode": "point", "at": (1.23, -2.5, 3.01)}
    assert "(1.23, -2.5, 3.01)" in probe.format_pick_reference("cube", pick)


def test_concave_edge_pick_is_flagged():
    """An L made of two boxes has an inward edge where polish is forbidden."""
    shape = Box(20, 10, 10) + Pos(5, 10, 0) * Box(10, 10, 10)
    ctx = Context()
    concave = concave_edges(shape)
    assert concave
    c = min(concave, key=lambda e: -e.length).center()
    pick = probe.resolve_pick(shape, ctx, "edge", (c.X, c.Y, c.Z))
    assert pick is not None
    assert pick["concave"] is True
    assert "concave edge" in probe.format_pick_reference("elbow", pick)
