/** Merge a viewer geometry pick into the chat message the user is about to send.

A pick alone is a valid message ("thicken this"); typed text follows the reference
so the agent sees the numbers first.
*/
export function mergePickReference(
  reference: string | null | undefined,
  text: string,
): string {
  const ref = (reference ?? "").trim();
  const body = text.trim();
  if (!ref) return body;
  if (!body) return ref;
  return `${ref}\n\n${body}`;
}
