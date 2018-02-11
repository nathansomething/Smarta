import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Chart } from 'angular-highcharts';

@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.css']
})
export class DetailComponent implements OnInit {

  private dataFrequency:string
  private id:Number;

  constructor(private route:ActivatedRoute) {
    this.dataFrequency = "Every Hour"
  }

  chart = new Chart({
    chart: {
      type: 'line'
    },
    title: {
      text: 'Traffic Over Time'
    },
    credits: {
      enabled: false
    },
    series: [{
      name: 'Days Ago',
      data: [1, 2, 3]
    }],
    yAxis: {
      title: {
        text: 'Number of Cars'
      }
    }
  });

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
  }
}
