
def dashboard():
    """ 
    a function that returns the home page
    Returns:  render_template: the home page
    """
    return render_template('home.html')

@app.route('/results', methods=['POST'])
def get_forecast():
    """ 
    a function that returns the results page
    Returns: render_template: the results page
    """
    location = request.form.get('location')
    if not location:
        abort(400, description="The 'location' field is required.")

    api_key = "3450acc3ccb969baf99ddbcb6796e04e"
    qapi_key = "f8f537204d2341b8292c06070ef4c6cd908686acbd6288bf1c4ea701ba90c2e5"

    units = request.form.get('units', 'imperial')  # Default to Fahrenheit if no unit is specified
    units_symbol = '°F' if units == 'imperial' else '°C' if units == 'metric' else 'K'