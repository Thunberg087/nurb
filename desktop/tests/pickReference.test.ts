import assert from "node:assert/strict";
import test from "node:test";
import { mergePickReference } from "../src/pickReference.ts";

test("returns the typed text when there is no pick", () => {
  assert.equal(mergePickReference(null, "make it taller"), "make it taller");
  assert.equal(mergePickReference("", "make it taller"), "make it taller");
});

test("sends the pick alone when the composer is empty", () => {
  assert.equal(
    mergePickReference("On bin, the face I selected is 10 mm2.", "  "),
    "On bin, the face I selected is 10 mm2.",
  );
});

test("puts the pick before the user's words", () => {
  assert.equal(
    mergePickReference("On bin, the face I selected is 10 mm2.", "thicken it"),
    "On bin, the face I selected is 10 mm2.\n\nthicken it",
  );
});
