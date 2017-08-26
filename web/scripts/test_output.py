output_ = io.StringIO()
output_.write('<html><body>')
output_.write('<style>{s}</style>'.format(s=open('notify/style.css').read()))

rows = []
colors = []
for text, true, predicted in d['output']:
    sentiments = {0: 'NEGATIVE', 1: 'NEUTRAL', 2: 'POSITIVE'}
    color = {True: 'rgba(0, 255, 0, 0.3);', False: 'rgba(255, 0, 0, 0.3);'}[true == predicted]
    true = sentiments[true]
    predicted = sentiments[predicted]
    rows.append([text, true, predicted])
    colors.append(color)

time = """<table><tr><td>Epoch {epoch_no} of {num_epochs} ({epoch_progress:.2f}%) complete</td>
<td>ELAPSED TIME:</td>
<td>REMAINING TIME:</td></tr><tr><td></td><td>{elapsed_time}</td><td>{remaining_time}</td></tr></table>"""
time = time.format(epoch_no=self._epoch_number,
                   num_epochs=self._total_epochs,
                   epoch_progress=self.epoch_percent,
                   elapsed_time=self.elapsed_time,
                   remaining_time=self.remaining_time)
output_.write(time)
output_.write("<p></p>")
output_.write("<p></p>")

accuracy = d['accuracy']
loss = d['loss']
stats = """<table><tr><td><b>LOSS:</b> {loss:.4f}</td><td style='text-align: right'><b>ACCURACY:</b> {accuracy:.2f}%</td></tr></table>"""
stats = stats.format(loss=loss, accuracy=100 * accuracy)
output_.write(stats)

output_.write("<p></p>")
output_.write(format_confusion_matrix({'NEGATIVE': 'NEGATIVE',
                                       'NEUTRAL': 'NEUTRAL',
                                       'POSITIVE': 'POSITIVE'},
                                      [x[1] for x in rows],
                                      [x[2] for x in rows]
                                      ))
output_.write("<p></p>")
output_.write(format_table(rows, ['Text', 'Truth', 'Predicted'], ['left', 'right', 'right'], sizes=[70, 15, 15], row_colors=colors))
output_.write('</body></html>')
ou = open('foo.html', 'w')
ou.write(output_.getvalue())
