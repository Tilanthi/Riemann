import statistics
batch1 = [0.346210, 0.357551, 0.392378, 0.403713, 0.414304, 0.447715, 0.469110, 0.531863, 0.583045, 0.607508]  # Letter 62, genus 2-4
batch2 = [0.161234, 0.219221, 0.226244, 0.269922, 0.294864, 0.335251, 0.336476]  # Letter 67, genus 5-7
combined = sorted(batch1 + batch2)
if __name__ == '__main__':
    print('n =', len(combined))
    print(combined)
    print('median =', statistics.median(combined))
