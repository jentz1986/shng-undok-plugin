# Frontier Silicon API for Python

Tested with Silvercrest, Hama, Technisat and Auna devices.

## Example Usage

```python
fs = FSAPI('http://10.149.158.82/device', 1234) # get the IP from your DHCP-Server/Router, 1234 is the default PIN for all my devices.

fs.volume = 12
fs.mode = 'dab'
fs.power = True

print 'Name: %s' % fs.friendly_name
print 'Version: %s' % fs.version
print 'Mute: %s' % fs.mute
print 'Mode: %s' % fs.mode
print 'Power: %s' % fs.power
print 'Volume: %s' % fs.volume
print 'Play status: %s' % fs.play_status
print 'Track name: %s' % fs.play_info_name
print 'Track text: %s' % fs.play_info_text
```
