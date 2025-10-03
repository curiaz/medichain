// Test for AI Health Button Functionality
// Run this in browser console to test the button behavior

console.log('=== AI Health Button Test ===');

// Function to test button state
function testButtonState() {
  const button = document.querySelector('.submit-button');
  const symptomsField = document.querySelector('textarea[placeholder*="symptoms"]');
  const ageSelect = document.querySelector('select');
  const genderInputs = document.querySelectorAll('input[type="radio"]');
  
  console.log('Button element:', button);
  console.log('Button disabled:', button?.disabled);
  console.log('Symptoms value:', symptomsField?.value);
  console.log('Age value:', ageSelect?.value);
  
  let genderValue = '';
  genderInputs.forEach(input => {
    if (input.checked) genderValue = input.value;
  });
  console.log('Gender value:', genderValue);
  
  const shouldBeDisabled = !symptomsField?.value.trim() || !ageSelect?.value || !genderValue;
  console.log('Should be disabled:', shouldBeDisabled);
  
  return {
    buttonDisabled: button?.disabled,
    shouldBeDisabled,
    isWorking: button?.disabled === shouldBeDisabled
  };
}

// Function to fill form and test
function fillFormAndTest() {
  console.log('\n=== Filling form to test button ===');
  
  // Fill symptoms
  const symptomsField = document.querySelector('textarea[placeholder*="symptoms"]');
  if (symptomsField) {
    symptomsField.value = 'Test symptoms - headache and fever';
    symptomsField.dispatchEvent(new Event('input', { bubbles: true }));
  }
  
  // Select age
  const ageSelect = document.querySelector('select');
  if (ageSelect) {
    ageSelect.value = 'Adult (18 - 64 years)';
    ageSelect.dispatchEvent(new Event('change', { bubbles: true }));
  }
  
  // Select gender
  const maleRadio = document.querySelector('input[value="Male"]');
  if (maleRadio) {
    maleRadio.checked = true;
    maleRadio.dispatchEvent(new Event('change', { bubbles: true }));
  }
  
  setTimeout(() => {
    console.log('\nAfter filling form:');
    const result = testButtonState();
    console.log('Test result:', result);
    
    if (result.isWorking) {
      console.log('✅ Button behavior is working correctly!');
    } else {
      console.log('❌ Button behavior issue detected');
    }
  }, 100);
}

// Run initial test
testButtonState();

// Auto-fill and test after 2 seconds
setTimeout(fillFormAndTest, 2000);