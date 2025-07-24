export function validateBoardForm(form: any) {
  const errors: any = {};
  if (!form.name || form.name.length < 3) errors.name = 'Name is required (min 3 chars)';
  if (!form.visibility) errors.visibility = 'Visibility is required';
  return errors;
} 